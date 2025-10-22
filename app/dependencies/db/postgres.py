from typing import Annotated, AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


async def get_postgres_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.postgres_manager.session_factory() as session:
        yield session


PostgresSessionAnn = Annotated[AsyncSession, Depends(get_postgres_session)]
