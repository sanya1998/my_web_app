"""
Первый запуск успешно отправляет сообщение.
Так как никто очередь не разгружает, сообщение там и остается.
Второй запуск уведомляет, что в очереди имеется дубликат, и не добавляет сообщение в очередь
"""

import asyncio

from app.common.logger import logger
from app.common.schemas.base import BaseSchema
from app.config.common import settings
from app.publishers.base import BasePublisher
from app.resources.rmq import BaseRabbitMQ


class Message(BaseSchema):
    message: str


async def main():
    logger.info("1. Creating RabbitMQ bindings...")
    async with BaseRabbitMQ() as base_rmq:
        await base_rmq.bind(
            settings.DEDUPLICATION_EXCHANGE_NAME,
            settings.DEDUPLICATION_QUEUE_NAME,
            settings.DEDUPLICATION_ROUTING_KEY,
            queue_arguments={"x-message-deduplication": True},
        )
    logger.info("2. Created RabbitMQ bindings.")

    logger.info("3. Publishing message...")
    async with BasePublisher(settings.DEDUPLICATION_EXCHANGE_NAME, settings.DEDUPLICATION_ROUTING_KEY) as publisher:
        await publisher.publish(Message(message="Hello!!!"), deduplication=True)
    logger.info("4. Published message.")


if __name__ == "__main__":
    asyncio.run(main())
