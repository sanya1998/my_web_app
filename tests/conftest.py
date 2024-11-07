from typing import AsyncIterator

import pytest
from app.app import app
from app.common.constants.environments import Environments
from app.common.tables.base import metadata
from app.config.main import settings
from app.resources.postgres import async_session, engine
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

ALLOWED_POSTGRES_HOSTS = ["localhost"]  # TODO: возможно, для ci/cd здесь понадобится postgres


@pytest.fixture(scope="session", autouse=True)
async def prepare_db():
    assert settings.ENVIRONMENT == Environments.TEST
    assert settings.POSTGRES_HOST in ALLOWED_POSTGRES_HOSTS

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
        with open("tests/data/dump.sql", "r") as f:
            commands = f.read()
        [await conn.execute(text(cmd)) for cmd in commands.split(sep=";") if cmd.strip()]


@pytest.fixture(scope="function")
async def session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session


@pytest.fixture(scope="function")
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app), base_url="http://test") as ac:
        yield ac
