from aio_pika import Message
from app.common.schemas.base import BaseSchema
from app.resources.rmq import BaseRabbitMQ
from orjson import orjson


class BasePublisher(BaseRabbitMQ):
    def __init__(self, exchange_name: str, routing_key: str = "", **kwargs):
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
    def prepare_message(
        raw_message: BaseSchema, exclude_unset=False, exclude_none=False, exclude_defaults=False
    ) -> Message:
        return Message(
            orjson.dumps(
                raw_message.model_dump(
                    exclude_unset=exclude_unset, exclude_none=exclude_none, exclude_defaults=exclude_defaults
                )
            )
        )

    async def ensure_connection(self):
        """Переподключается при разрыве соединения"""
        if self.connection is None or self.connection.is_closed:
            await self.setup()

    async def publish(
        self, message: BaseSchema, exclude_unset=False, exclude_none=False, exclude_defaults=False
    ) -> None:
        await self.ensure_connection()
        prepared_message = self.prepare_message(
            message, exclude_unset=exclude_unset, exclude_none=exclude_none, exclude_defaults=exclude_defaults
        )
        await self.exchange.publish(message=prepared_message, routing_key=self.routing_key)
