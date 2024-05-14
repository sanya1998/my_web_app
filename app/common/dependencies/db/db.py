from typing import Annotated, AsyncIterator

from app.resources.db import async_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
