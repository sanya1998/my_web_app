import asyncio

import click
from aio_pika import ExchangeType
from app.common.logger import logger
from app.config.common import settings
from app.resources.rmq import BaseRabbitMQ


@click.group()
def cli() -> None:
    pass


async def create_rmq_reindex_async() -> None:
    logger.info("Creating RabbitMQ binding...")
    async with BaseRabbitMQ() as base_rmq:
        await base_rmq.bind(
            settings.ES_WRITE_EXCHANGE_NAME, settings.ES_WRITE_REINDEX_QUEUE_NAME, exchange_type=ExchangeType.FANOUT
        )
    logger.info("Created RabbitMQ binding.")


@cli.command()
def create_rmq_reindex() -> None:
    asyncio.run(create_rmq_reindex_async())


async def delete_rmq_reindex_async() -> None:
    logger.info("Deleting RabbitMQ binding...")
    async with BaseRabbitMQ() as base_rmq:
        await base_rmq.channel.queue_delete(queue_name=settings.ES_WRITE_REINDEX_QUEUE_NAME)
    logger.info("Deleted RabbitMQ binding.")


@cli.command()
def delete_rmq_reindex() -> None:
    asyncio.run(delete_rmq_reindex_async())


if __name__ == "__main__":
    cli()
