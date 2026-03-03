import hashlib

from aio_pika import Message, RobustExchange
from aiormq import DeliveryError
from app.common.logger import logger
from app.common.schemas.base import BaseSchema
from app.resources.rmq import BaseRabbitMQ
from orjson import orjson


class BasePublisher(BaseRabbitMQ):
    def __init__(self, exchange_name: str, routing_key: str = "", **kwargs):
        self.routing_key = routing_key
        self.exchange_name = exchange_name
        self.exchange: RobustExchange | None = None
        super().__init__(**kwargs)

    async def set_exchange(self):
        self.exchange = await self.channel.get_exchange(name=self.exchange_name)
        return self.exchange

    async def setup(self):
        await super().setup()
        await self.set_exchange()

    @staticmethod
    def prepare_message(
        raw_message: BaseSchema, exclude_unset=False, exclude_none=False, exclude_defaults=False, deduplication=False
    ) -> Message:
        body = orjson.dumps(
            raw_message.model_dump(
                exclude_unset=exclude_unset, exclude_none=exclude_none, exclude_defaults=exclude_defaults
            )
        )
        headers = dict()
        if deduplication:
            headers["x-deduplication-header"] = hashlib.md5(body).hexdigest()
        return Message(body=body, headers=headers if headers else None)

    async def ensure_connection(self):
        """Переподключается при разрыве соединения"""
        if self.connection is None or self.connection.is_closed:
            await self.setup()

    async def publish(
        self, message: BaseSchema, exclude_unset=False, exclude_none=False, exclude_defaults=False, deduplication=False
    ) -> None:
        await self.ensure_connection()
        prepared_message = self.prepare_message(
            message,
            exclude_unset=exclude_unset,
            exclude_none=exclude_none,
            exclude_defaults=exclude_defaults,
            deduplication=deduplication,
        )
        try:
            await self.exchange.publish(message=prepared_message, routing_key=self.routing_key)
        except DeliveryError as e:
            if "Basic.Nack" in str(e):
                logger.warning("Сообщение отклонено (дубликат)")
            else:
                raise
