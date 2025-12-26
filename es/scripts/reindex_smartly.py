"""
🔹 Миграция индекса
1. Обновить es/indices/products.yaml
2. Заполнить поле BASE_ALIAS
3. Выполнить скрипт `python3 reindex_smartly.py start_reindex`
4. Выполнить скрипт `python3 reindex_smartly.py end_reindex`
"""

import asyncio

import click
from app.config.common import settings
from es.clients.index import IndexClient

BASE_ALIAS = settings.ES_PRODUCTS_BASE_ALIAS


@click.group()
def cli() -> None:
    pass


async def start_reindex_async() -> None:
    async with IndexClient(hosts=settings.ES_HOSTS) as client:
        client: IndexClient
        task_id = await client.start_reindex(base_alias=BASE_ALIAS)
        print(f"Task ID: {task_id}")


@cli.command()
def start_reindex() -> None:
    asyncio.run(start_reindex_async())


async def end_reindex_async() -> None:
    async with IndexClient(hosts=settings.ES_HOSTS) as client:
        client: IndexClient
        await client.end_reindex(base_alias=BASE_ALIAS, check_interval=2)


@cli.command()
def end_reindex() -> None:
    asyncio.run(end_reindex_async())


if __name__ == "__main__":
    cli()
