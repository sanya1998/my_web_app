from app.config.main import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(
    url=settings.DB_URL,
    # json_serializer=lambda val: json.dumps(val, default=str),
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
