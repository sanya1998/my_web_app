from typing import Annotated, AsyncIterator

from app.resources.postgres import async_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_postgres_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session


PostgresSessionDep = Annotated[AsyncSession, Depends(get_postgres_session)]
