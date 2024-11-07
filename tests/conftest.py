import os

import pytest
from app.common.tables.base import metadata
from app.config.main import settings
from app.resources.postgres import async_session, engine
from sqlalchemy import text

os.environ["ENVIRONMENT"] = "test"

ALLOWED_POSTGRES_HOSTS = ["localhost"]  # TODO: возможно, для ci/cd здесь понадобится postgres


@pytest.fixture(scope="session", autouse=True)
async def prepare_postgres():
    assert settings.POSTGRES_HOST in ALLOWED_POSTGRES_HOSTS

    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)

    async with async_session() as session:
        with open("tests/data/dump.sql", "r") as f:
            commands = f.read()
        [await session.execute(text(cmd)) for cmd in commands.split(sep=";") if cmd.strip()]
        await session.commit()
