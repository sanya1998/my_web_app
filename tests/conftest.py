from typing import AsyncIterator

import pytest_asyncio
from app.app import app
from app.common.constants.environments import Environments
from app.common.schemas.user import OneUserReadSchema
from app.common.tables.base import metadata
from app.config.main import settings
from app.resources.postgres import async_session, engine
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

ALLOWED_POSTGRES_HOSTS = ["localhost"]  # TODO: возможно, для ci/cd здесь понадобится postgres


@pytest_asyncio.fixture(loop_scope="session", scope="session", autouse=True)
async def prepare_db():
    assert settings.ENVIRONMENT == Environments.TEST
    assert settings.POSTGRES_HOST in ALLOWED_POSTGRES_HOSTS

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
        with open("tests/data/dump.sql", "r") as f:
            commands = f.read()
        [await conn.execute(text(cmd)) for cmd in commands.split(sep=";") if cmd.strip()]


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def session() -> AsyncIterator[AsyncSession]:
    async with async_session() as _session:
        yield _session


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        yield ac


async def sign_in(client: AsyncClient, email: str, raw_password: str):
    """
    Аутентифицирует пользователя и возвращает его
    """
    response_sign_in = await client.post("/api/v1/users/sign_in", data=dict(email=email, raw_password=raw_password))
    assert response_sign_in.status_code == status.HTTP_200_OK

    response_user = await client.get("/api/v1/users/current")
    assert response_user.status_code == status.HTTP_200_OK
    return OneUserReadSchema.model_validate(response_user.json())


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def admin_user(client: AsyncClient) -> OneUserReadSchema:
    """
    Аутентификация пользователя с правами админа
    """
    return await sign_in(client=client, email="fedor@moloko.ru", raw_password="hard_password")


@pytest_asyncio.fixture(loop_scope="function", scope="function")
async def user(client: AsyncClient) -> OneUserReadSchema:
    """
    Аутентификация обычного пользователя
    """
    return await sign_in(client=client, email="sharik@moloko.ru", raw_password="easy_password")
