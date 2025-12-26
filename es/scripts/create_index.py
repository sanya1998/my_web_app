"""
🔹 Первое создание индекса
1. Создать файл конфигурации es/indices/products.yaml
2. Заполнить поле BASE_ALIAS
3. Выполнить скрипт `python3 create_index.py`
"""

from app.config.common import settings
from es.clients.index import IndexClient

BASE_ALIAS = settings.ES_PRODUCTS_BASE_ALIAS


async def main():
    async with IndexClient(hosts=settings.ES_HOSTS) as client:
        client: IndexClient
        await client.create_first_index(base_alias=BASE_ALIAS)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
