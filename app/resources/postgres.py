import json

import pydantic.json
from app.common.constants.environments import Environments
from app.config.common import settings
from sqlalchemy import AsyncAdaptedQueuePool, NullPool
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(
    url=settings.POSTGRES_URL,
    poolclass=NullPool if settings.ENVIRONMENT == Environments.TEST else AsyncAdaptedQueuePool,
    json_serializer=lambda *args, **kwargs: json.dumps(*args, default=pydantic.json.pydantic_encoder, **kwargs),
    # pool_size=settings.DB_POOL_SIZE,
    # max_overflow=settings.DB_MAX_OVERFLOW,
    # pool_recycle=settings.DB_POOL_RECYCLE,
    # pool_pre_ping=settings.DB_POOL_PRE_PING,
    # echo=settings.DEBUG,
)
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    # autocommit=False,
    autoflush=True,
)


def with_session(func):
    """
    @with_session
    async def func(arg, session, kwarg=None):
        await session.execute("select * from table limit 2")

    await func(1, kwarg=2)
    """

    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(*args, session=session, **kwargs)
        # try:
        #     ...
        # except Exception:
        #     # TODO: await session.rollback()
        #     raise

    return wrapper
