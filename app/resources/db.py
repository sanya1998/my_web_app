from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config.main import settings

engine = create_async_engine(
    url=settings.DB_URL,
    # echo=settings.DEBUG,
)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    # autocommit=False,
    # autoflush=True,
)
