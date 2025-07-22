import pickle
from typing import Any

from aio_pika import Message
from app.config.common import settings
from app.resources.rmq.base import BaseRabbitMQ


class BasePublisher(BaseRabbitMQ):
    def __init__(self, routing_key: str, exchange_name: str, **kwargs):
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        super().__init__(**kwargs)

    @staticmethod
    def prepare_message(raw_message: Any) -> Message:
        return Message(pickle.dumps(raw_message, protocol=settings.PICKLE_PROTOCOL))

    async def publish(self, message: Any) -> None:
        prepared_message = self.prepare_message(message)
        exchange = await self.channel.get_exchange(name=self.exchange_name)
        await exchange.publish(message=prepared_message, routing_key=self.routing_key)
