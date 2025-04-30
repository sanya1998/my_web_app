from typing import Any, AsyncGenerator, AsyncIterator

import pytest_asyncio
from app.app import app
from app.common.constants.environments import Environments
from app.common.tables.base import metadata
from app.config.common import settings
from app.resources.postgres import async_session, engine
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from tests.constants import BASE_USERS_URL

ALLOWED_POSTGRES_HOSTS = ["0.0.0.0"]  # TODO: возможно, для тестов в ci/cd здесь понадобится postgres, redis


@pytest_asyncio.fixture(loop_scope="session", scope="session", autouse=True)
async def prepare_db():
    assert settings.ENVIRONMENT == Environments.TEST
    assert settings.POSTGRES_HOST in ALLOWED_POSTGRES_HOSTS
    assert settings.REDIS_HOST in ALLOWED_POSTGRES_HOSTS

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
async def client() -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        yield ac


# TODO: в идеале использовать только client, но при этом должен отрабатывать test_multy_clients
client_for_admin = client_for_manager = client_for_moderator = client_for_user = client


async def sign_in(client: AsyncClient, email: str, password: str, expected_status=status.HTTP_200_OK):
    """
    Аутентифицирует пользователя
    """
    response_sign_in = await client.post(f"{BASE_USERS_URL}sign_in", data=dict(email=email, password=password))
    assert response_sign_in.status_code == expected_status


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def admin_client(client_for_admin: AsyncClient) -> AsyncClient:
    """
    Аутентификация пользователя с правами админа
    """
    await sign_in(client=client_for_admin, email="fedor@moloko.ru", password="hard_password")
    return client_for_admin


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def manager_client(client_for_manager: AsyncClient) -> AsyncClient:
    """
    Аутентификация пользователя с правами менеджера
    """
    await sign_in(client=client_for_manager, email="kot@pes.ru", password="easy_password")
    return client_for_manager


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def moderator_client(client_for_moderator: AsyncClient) -> AsyncClient:
    """
    Аутентификация пользователя с правами менеджера
    """
    await sign_in(client=client_for_moderator, email="mod@mod.ru", password="easy_password")
    return client_for_moderator


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def user_client(client_for_user: AsyncClient) -> AsyncClient:
    """
    Аутентификация обычного пользователя
    """
    await sign_in(client=client_for_user, email="sharik@moloko.ru", password="easy_password")
    return client_for_user


@pytest_asyncio.fixture(loop_scope="function", scope="function")
def mock_send_email(mocker):
    def fake_send_email(booking: dict, email_to: str):
        print(f"Имитация отправки сообщения на почту {email_to}. {booking}.")

    # TODO: рассмотреть with mock.patch("app.common.tasks.email.send_booking_notify_email.delay") as fake_send_email
    mocker.patch("app.common.tasks.email.send_booking_notify_email.delay", fake_send_email)
