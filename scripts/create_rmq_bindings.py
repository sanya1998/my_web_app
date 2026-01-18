import asyncio

from aio_pika import ExchangeType
from app.common.logger import logger
from app.config.common import settings
from app.resources.rmq import BaseRabbitMQ


async def main():
    logger.info("Creating RabbitMQ bindings...")
    async with BaseRabbitMQ() as base_rmq:
        await base_rmq.bind(settings.HISTORY_EXCHANGE_NAME, settings.HISTORY_QUEUE_NAME, settings.HISTORY_ROUTING_KEY)
        await base_rmq.bind(settings.SSE_EXCHANGE_NAME, settings.SSE_QUEUE_NAME, settings.SSE_ROUTING_KEY)
        await base_rmq.bind(
            settings.ES_WRITE_EXCHANGE_NAME, settings.ES_WRITE_QUEUE_NAME, exchange_type=ExchangeType.FANOUT
        )
    logger.info("Created RabbitMQ bindings.")


if __name__ == "__main__":
    asyncio.run(main())
