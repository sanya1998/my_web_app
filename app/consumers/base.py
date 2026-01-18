import asyncio
import logging
from typing import Generic, Optional, Type, TypeVar

from aio_pika.abc import AbstractIncomingMessage
from app.common.helpers.stop_events import configure_event_of_stop_signal
from app.common.schemas.base import BaseSchema
from app.config.common import settings
from app.resources.rmq import BaseRabbitMQ
from orjson import JSONDecodeError, orjson

logger = logging.getLogger(__name__)

MessageClass = TypeVar("MessageClass", bound=BaseSchema)


class BaseConsumer(BaseRabbitMQ, Generic[MessageClass]):
    """
    Patterns:
    from pydantic import BaseModel

    class MessageModel(BaseModel):
        pass

    class Consumer(BaseConsumer[MessageModel]):
        message_cls = MessageModel
        async def process_message(self, message):
            message: MessageModel = await super().process_message(message)
            print(f"Message: {message}")

    # 1) blocking consumer
    consumer = Consumer(queue_name="queue_name")
    asyncio.run(consumer.blocking_consume())

    # 2) async consumer
    async with Consumer(queue_name="queue_name") as consumer:
        await consumer.consume()
        # Stop, for example: `await asyncio.Future()`
        # Stop, for another example in FastApi lifespan: 'yield'
    """

    message_cls: Type[BaseSchema] = MessageClass
    ack_exceptions = (JSONDecodeError,)

    def __init__(self, queue_name: str = "", **kwargs):
        self.queue_name: str = queue_name
        self.stop_event: Optional[asyncio.Event] = None  # Используется только в блокирующем режиме
        super().__init__(**kwargs)

    async def on_message(self, message: AbstractIncomingMessage) -> None:
        """Обработка входящего сообщения"""
        try:
            await self.process_message(message)
        except self.ack_exceptions as e:
            logger.warning(f"Ack exception while processing message: {message.body}. Exc: {e}")
            await message.ack()
        except Exception as e:
            logger.error(f"Exception while processing message: {message.body}. Exc: {e}")
            # Можно добавить dead letter queue или повторную обработку
        else:
            await message.ack()

    async def process_message(self, message: AbstractIncomingMessage) -> MessageClass:
        """Преобразование сырого сообщения в Pydantic модель"""
        parsed_message = self.message_cls.model_validate(orjson.loads(message.body))
        return parsed_message

    async def __consume(self, prefetch_count=settings.RMQ_PREFETCH_COUNT_DEFAULT):
        """Внутренний метод для начала потребления сообщений"""
        await self.channel.set_qos(prefetch_count=prefetch_count)
        queue = await self.channel.get_queue(name=self.queue_name)
        await queue.consume(self.on_message)

    async def consume(self, prefetch_count=settings.RMQ_PREFETCH_COUNT_DEFAULT):
        """Асинхронный запуск потребителя (работает в фоне)"""
        if not self.connection or not self.channel:
            raise RuntimeError("RabbitMQ connection or channel are not initialized.")

        await self.__consume(prefetch_count=prefetch_count)
        logger.info(f"Consumer {self.queue_name}: async mode started")
        logger.info("[*] Don't forget to shutdown consumer.")

    async def blocking_consume(self, prefetch_count=settings.RMQ_PREFETCH_COUNT_DEFAULT):
        """Блокирующий запуск потребителя (работает до сигнала остановки)"""
        self.stop_event = configure_event_of_stop_signal()
        async with self:
            await self.__consume(prefetch_count=prefetch_count)
            logger.info(f"Consumer {self.queue_name}: blocking mode started")
            logger.info("[*] To exit press CTRL+C.")
            try:
                await self.stop_event.wait()
            except KeyboardInterrupt:
                logger.info("Received Ctrl+C, shutting down...")
            finally:
                logger.info(f"Consumer {self.queue_name}: stopped gracefully.")

    async def stop(self):
        """Принудительная остановка потребителя"""
        if self.stop_event:
            self.stop_event.set()
        logger.info(f"Consumer {self.queue_name}: manual stop requested")
