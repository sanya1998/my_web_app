import os
from functools import wraps
from typing import AsyncIterator
from urllib.parse import urlparse

import pytest
import sqlparse
from app.app import app as _app
from app.common.constants.environments import Environments
from app.common.constants.roles import AllRolesEnum
from app.common.logger import logger
from app.config.common import settings
from app.dependencies.auth.credentials import CredentialsInput
from app.resources.postgres import PostgresManager
from asgi_lifespan import LifespanManager
from es.clients.index import IndexESClient
from es.clients.pydantic_ import PydanticESClient
from es.dsl.indices.products import ProductDocument
from es.dsl.indices.reindex_history import ReindexHistoryDocument
from httpx import ASGITransport, Response
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from tests.common import CustomAsyncClient
from tests.constants.urls import AUTH_SIGN_IN_URL
from tests.constants.users_info import CREDENTIALS
from tests.dump.es_dump import generate_and_index_test_data

ALLOWED_POSTGRES_HOSTS = ["0.0.0.0"]  # TODO: возможно, для тестов в ci/cd здесь понадобится postgres, redis
ALLOWED_REDIS_HOSTS = ["0.0.0.0"]


@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    """Почему-то без этой фикстуры тесты пропускаются, хотя выносил в ini `anyio_mode = "auto"`"""
    return "asyncio"


@pytest.fixture(scope="session")
async def postgres_manager() -> AsyncIterator[PostgresManager]:
    async with PostgresManager() as manager:
        yield manager


@pytest.fixture(scope="session", autouse=True)
async def prepare_postgres(postgres_manager):
    assert settings.ENVIRONMENT == Environments.TEST
    assert settings.POSTGRES_HOST in ALLOWED_POSTGRES_HOSTS
    assert settings.REDIS_HOST in ALLOWED_REDIS_HOSTS  # TODO: не здесь надо проверять

    os.system("alembic downgrade base")
    os.system("alembic upgrade head")

    with open("tests/dump/db_dump.sql", "r") as f:
        sql_content = f.read()

    commands = sqlparse.split(sql_content)

    async with postgres_manager.engine.begin() as conn:
        for cmd in commands:
            if cmd.strip():
                await conn.execute(text(cmd))


@pytest.fixture
async def postgres_session(postgres_manager: PostgresManager) -> AsyncIterator[AsyncSession]:
    async with postgres_manager.session_factory() as session:
        yield session


def check_es_hosts():
    assert all(urlparse(host).hostname in ALLOWED_POSTGRES_HOSTS for host in settings.ES_HOSTS)


@pytest.fixture(scope="session", autouse=True)
async def prepare_elasticsearch():
    assert settings.ENVIRONMENT == Environments.TEST
    check_es_hosts()
    async with IndexESClient(hosts=settings.ES_HOSTS) as _es_client:
        _es_client: IndexESClient
        indices = [ReindexHistoryDocument, ProductDocument]
        for document_class in indices:
            # TODO: не удаляются предыдущие версии
            await _es_client.delete_index(document_class=document_class)
            await _es_client.create_first_index(document_class=document_class)

    # TODO: дублируется здесь и es_client
    # async with PydanticESClient(
    #     hosts=settings.ES_HOSTS,
    #     base_alias=settings.ES_PRODUCTS_BASE_ALIAS,
    #     use_write_alias=True
    # ) as _es_client:
    #     _es_client: PydanticESClient
    #     await generate_and_index_test_data(_es_client)

    async with PydanticESClient(
        hosts=settings.ES_HOSTS, base_alias=settings.ES_PRODUCTS_BASE_ALIAS, use_write_alias=False
    ) as _es_client:
        _es_client: PydanticESClient
        await generate_and_index_test_data(_es_client)


@pytest.fixture
async def es_client() -> AsyncIterator[PydanticESClient]:
    assert settings.ENVIRONMENT == Environments.TEST
    check_es_hosts()
    # TODO: дублируется async with PydanticESClient(
    async with PydanticESClient(hosts=settings.ES_HOSTS) as _es_client:
        yield _es_client


@pytest.fixture(scope="session")
async def app():
    async with LifespanManager(_app) as manager:
        yield manager.app


async def sign_in(new_client: CustomAsyncClient, email: str, password: str, code=status.HTTP_200_OK) -> Response:
    """Аутентифицирует клиента"""
    user_data = CredentialsInput(username=email, password=SecretStr(password)).model_dump()
    return await new_client.post(AUTH_SIGN_IN_URL, data=user_data, code=code)


def auth_client_fixture(role: AllRolesEnum = None):
    def decorator(fixture_func):
        @wraps(fixture_func)
        @pytest.fixture
        async def wrapper(app):
            async with CustomAsyncClient(transport=ASGITransport(app), base_url="http://test") as new_client:
                if role:
                    email, password = CREDENTIALS[role]
                    await sign_in(new_client=new_client, email=email, password=password)

                # Вариант с кастомизацией клиента внутри фикстуры:
                # async for result in fixture_func(new_client):
                #     yield result

                # Текущий простой вариант:
                yield new_client

        return wrapper

    return decorator


# Вариант с кастомизацией (закомментирован на будущее):
# @auth_client_fixture(AllRolesEnum.ADMIN)
# async def admin_client(new_client: CustomAsyncClient) -> AsyncIterator[CustomAsyncClient]:
#     # new_client.default_headers["X-Admin"] = "true"
#     # new_client.timeout = 30.0
#     yield new_client


# Текущий вариант
@auth_client_fixture(AllRolesEnum.ADMIN)
async def admin_client() -> AsyncIterator[CustomAsyncClient]:
    pass


@auth_client_fixture(AllRolesEnum.MANAGER)
async def manager_client() -> AsyncIterator[CustomAsyncClient]:
    pass


@auth_client_fixture(AllRolesEnum.MODERATOR)
async def moderator_client() -> AsyncIterator[CustomAsyncClient]:
    pass


@auth_client_fixture(AllRolesEnum.USER)
async def user_client() -> AsyncIterator[CustomAsyncClient]:
    pass


@auth_client_fixture()
async def client() -> AsyncIterator[CustomAsyncClient]:
    pass


@pytest.fixture
def mock_send_email(mocker):
    def fake_send_email(booking: dict, email_to: str):
        logger.info(f"Имитация отправки сообщения на почту {email_to}. {booking}.")

    # TODO: рассмотреть with mock.patch("app.tasks.email.send_booking_notify_email.delay") as fake_send_email
    mocker.patch("app.tasks.email.send_booking_notify_email.delay", fake_send_email)
