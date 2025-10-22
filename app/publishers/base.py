from aio_pika import Message
from app.common.schemas.base import BaseSchema
from app.resources.rmq import BaseRabbitMQ
from orjson import orjson


class BasePublisher(BaseRabbitMQ):
    def __init__(self, routing_key: str, exchange_name: str, **kwargs):
        self.routing_key = routing_key
        self.exchange_name = exchange_name
        self.exchange = None
        super().__init__(**kwargs)

    async def set_exchange(self):
        self.exchange = await self.channel.get_exchange(name=self.exchange_name)
        return self.exchange

    async def setup(self):
        await super().setup()
        await self.set_exchange()

    @staticmethod
    def prepare_message(raw_message: BaseSchema) -> Message:
        return Message(orjson.dumps(raw_message.model_dump()))

    async def ensure_connection(self):
        """Переподключается при разрыве соединения"""
        if self.connection is None or self.connection.is_closed:
            await self.setup()

    async def publish(self, message: BaseSchema) -> None:
        await self.ensure_connection()
        prepared_message = self.prepare_message(message)
        await self.exchange.publish(message=prepared_message, routing_key=self.routing_key)
