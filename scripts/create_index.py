"""
🔹 Первое создание индекса
1. Создать DSL модель в es/dsl/indices/products.py
2. Прописать нужную модель в DOCUMENT_CLASS = ProductDocument
3. Выполнить скрипт `python3 create_index.py`
"""

import asyncio

from app.config.common import settings
from es.clients.index import IndexESClient
from es.dsl.indices.products import ProductDocument

DOCUMENT_CLASS = ProductDocument


async def main():
    async with IndexESClient(hosts=settings.ES_HOSTS) as client:
        client: IndexESClient
        index_name = await client.create_first_index(DOCUMENT_CLASS)
        print(f"Created index: {index_name}")


if __name__ == "__main__":
    asyncio.run(main())
