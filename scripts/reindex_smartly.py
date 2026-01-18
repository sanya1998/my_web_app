"""
🔹 Миграция индекса
1. Обновить DSL модель (изменить версию в Index.name)
2. Прописать нужную модель в DOCUMENT_CLASS = ProductDocument
3. Убедиться,
    что не запущен доп консьюмер для двойной записи,
    что очередь для для двойной записи не существует,
    что нет индексов с алиасом `{base_alias}_write`.
4. Выполнить скрипт `python3 reindex_smartly.py prepare-reindex` (Создается новый индекс с алиасом `{base_alias}_write`)
5. ! Настроить параллельную запись в `{base_alias}` и `{base_alias}_write` (Например, запуск доп консьюмера для второго)
    `python3 rmq_reindex.py create-rmq-reindex`
    `python3 manage.py run-es-write-reindex-consumer`
6. Выполнить скрипт `python3 reindex_smartly.py start-reindex` (Реиндексация документов в новый индекс)
7. Выполнить скрипт `python3 reindex_smartly.py end-reindex`
    - Ожидается завершение реиндекса
    - Переключение алиасов `{base_alias}` на новый индекс и `{base_alias}_write` на старый индекс
8. ! Остановить параллельную запись в `{base_alias}_write`:
    `python3 rmq_reindex.py delete-rmq-reindex`
    ! остановить run-es-write-reindex-consumer
    ! Удалить алиас `{base_alias}_write`
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


async def prepare_reindex_async() -> None:
    async with IndexESClient(hosts=settings.ES_HOSTS) as client:
        client: IndexESClient
        await client.prepare_reindex(DOCUMENT_CLASS)


@cli.command()
def prepare_reindex() -> None:
    asyncio.run(prepare_reindex_async())


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
