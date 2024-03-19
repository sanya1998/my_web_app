

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config.db import db_settings

DATABASE_URL = (
    f"{db_settings.DB_DRIVER}"
    f"://{db_settings.DB_USER}:{db_settings.DB_PASSWORD}"
    f"@{db_settings.DB_HOST}:{db_settings.DB_PORT}"
    f"/{db_settings.DB_NAME}"
)

engine = create_async_engine(url=DATABASE_URL)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


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
