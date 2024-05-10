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


# временный код, демонстрирующий успешную работу (убрать в следующем коммите)
async def async_main():
    from sqlalchemy import select

    from app.common.tables.hotels import Hotels

    async with engine.connect() as conn:
        result = await conn.stream(select(Hotels))
        async for row in result:
            print("row: %s" % (row,))

    async with async_session() as session:
        result = await session.execute(select(Hotels))
        row = result.scalars().first()
        print("row: %s" % (row.name))


if __name__ == "__main__":
    import asyncio

    asyncio.run(async_main())
