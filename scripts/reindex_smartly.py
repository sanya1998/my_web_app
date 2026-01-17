# scripts/reindex_smartly.py
"""
🔹 Миграция индекса
1. Обновить DSL модель (изменить версию в Index.name)
2. Прописать нужную модель в DOCUMENT_CLASS = ProductDocument
3. Выполнить скрипт `python3 reindex_smartly.py start_reindex`
4. Выполнить скрипт `python3 reindex_smartly.py end_reindex`
"""

import asyncio

import click
from app.config.common import settings
from es.clients.index import IndexESClient
from es.dsl.indices.products import ProductDocument

DOCUMENT_CLASS = ProductDocument


@click.group()
def cli() -> None:
    pass


async def start_reindex_async() -> None:
    async with IndexESClient(hosts=settings.ES_HOSTS) as client:
        client: IndexESClient
        task_id = await client.start_reindex(DOCUMENT_CLASS)
        print(f"Task ID: {task_id}")


@cli.command()
def start_reindex() -> None:
    asyncio.run(start_reindex_async())


async def end_reindex_async() -> None:
    async with IndexESClient(hosts=settings.ES_HOSTS) as client:
        client: IndexESClient
        await client.end_reindex(DOCUMENT_CLASS, check_interval=2)


@cli.command()
def end_reindex() -> None:
    asyncio.run(end_reindex_async())


if __name__ == "__main__":
    cli()
