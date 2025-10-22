import json

import pydantic.json
from app.config.common import settings
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool


class PostgresManager:
    """Manages asynchronous DB sessions with lazy initialization."""

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    @classmethod
    def new_engine(cls):
        return create_async_engine(
            url=settings.POSTGRES_URL,
            poolclass=AsyncAdaptedQueuePool,
            json_serializer=lambda *args, **kwargs: json.dumps(*args, default=pydantic.json.pydantic_encoder, **kwargs),
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_pre_ping=settings.DB_POOL_PRE_PING,
            # TODO: изучить вопрос echo=settings.DEBUG,
        )

    @classmethod
    def new_session_factory(cls, bind: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            bind=bind,
            expire_on_commit=False,  # False: экземпляры останутся доступными на время транзакции после вызова commit()
            autoflush=True,  # True: автоматически синхронизирует не обработанные изменения после каждой операции.
            class_=AsyncSession,
        )

    @property
    def engine(self) -> AsyncEngine:
        """Lazy initialization of engine"""
        if self._engine is None:
            self._engine = self.new_engine()
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Lazy initialization of session factory"""
        if self._session_factory is None:
            self._session_factory = self.new_session_factory(self.engine)
        return self._session_factory

    async def shutdown(self) -> None:
        """Dispose of the database engine."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()
