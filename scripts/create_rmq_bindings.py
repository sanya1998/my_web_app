import asyncio

from app.common.logger import logger
from app.config.common import settings
from app.resources.rmq.base import BaseRabbitMQ


async def main():
    logger.info("Creating RabbitMQ bindings for History...")
    async with BaseRabbitMQ() as base_rmq:
        await base_rmq.bind(settings.HISTORY_EXCHANGE_NAME, settings.HISTORY_QUEUE_NAME, settings.HISTORY_ROUTING_KEY)
    logger.info("Created RabbitMQ bindings for History")


if __name__ == "__main__":
    asyncio.run(main())
