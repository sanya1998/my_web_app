from typing import Any, AsyncGenerator, AsyncIterator

import pytest_asyncio
from app.app import app
from app.common.constants.environments import Environments
from app.common.logger import logger
from app.common.tables.base import metadata
from app.config.common import settings
from app.dependencies.auth.credentials import CredentialsInput
from app.resources.postgres import async_session, engine
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, Response
from pydantic import SecretStr
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from tests.common import TestClient
from tests.constants.urls import AUTH_SIGN_IN_URL
from tests.constants.users_info import (
    ADMIN_EMAIL,
    ADMIN_PASSWORD,
    MANAGER_EMAIL,
    MANAGER_PASSWORD,
    MODERATOR_EMAIL,
    MODERATOR_PASSWORD,
    USER_EMAIL,
    USER_PASSWORD,
)

ALLOWED_POSTGRES_HOSTS = ["0.0.0.0"]  # TODO: возможно, для тестов в ci/cd здесь понадобится postgres, redis
ALLOWED_REDIS_HOSTS = ["0.0.0.0"]


@pytest_asyncio.fixture(loop_scope="session", scope="session", autouse=True)
async def prepare_db():
    assert settings.ENVIRONMENT == Environments.TEST
    assert settings.POSTGRES_HOST in ALLOWED_POSTGRES_HOSTS
    assert settings.REDIS_HOST in ALLOWED_REDIS_HOSTS

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
        with open("tests/dump/dump.sql", "r") as f:
            commands = f.read()
        [await conn.execute(text(cmd)) for cmd in commands.split(sep=";") if cmd.strip()]


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def session() -> AsyncIterator[AsyncSession]:
    async with async_session() as _session:
        yield _session


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def client() -> AsyncGenerator[TestClient, Any]:
    async with TestClient(transport=ASGITransport(app), base_url="http://test") as ac, LifespanManager(app):
        yield ac


# TODO: в идеале использовать только client, но при этом должен отрабатывать test_multy_clients
client_for_admin = client_for_manager = client_for_moderator = client_for_user = client


async def sign_in(client: TestClient, email: str, password: str, code=status.HTTP_200_OK) -> Response:
    """
    Аутентифицирует пользователя
    """
    user_data = CredentialsInput(username=email, password=SecretStr(password)).model_dump()
    return await client.post(AUTH_SIGN_IN_URL, data=user_data, code=code)


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def admin_client(client_for_admin: TestClient) -> TestClient:
    """
    Аутентификация пользователя с правами админа
    """
    await sign_in(client=client_for_admin, email=ADMIN_EMAIL, password=ADMIN_PASSWORD)
    return client_for_admin


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def manager_client(client_for_manager: TestClient) -> TestClient:
    """
    Аутентификация пользователя с правами менеджера
    """
    await sign_in(client=client_for_manager, email=MANAGER_EMAIL, password=MANAGER_PASSWORD)
    return client_for_manager


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def moderator_client(client_for_moderator: TestClient) -> TestClient:
    """
    Аутентификация пользователя с правами модератора
    """
    await sign_in(client=client_for_moderator, email=MODERATOR_EMAIL, password=MODERATOR_PASSWORD)
    return client_for_moderator


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def user_client(client_for_user: TestClient) -> TestClient:
    """
    Аутентификация обычного пользователя
    """
    await sign_in(client=client_for_user, email=USER_EMAIL, password=USER_PASSWORD)
    return client_for_user


@pytest_asyncio.fixture(loop_scope="function", scope="function")
def mock_send_email(mocker):
    def fake_send_email(booking: dict, email_to: str):
        logger.info(f"Имитация отправки сообщения на почту {email_to}. {booking}.")

    # TODO: рассмотреть with mock.patch("app.tasks.email.send_booking_notify_email.delay") as fake_send_email
    mocker.patch("app.tasks.email.send_booking_notify_email.delay", fake_send_email)
