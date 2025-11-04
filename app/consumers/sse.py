import logging

from aio_pika.abc import AbstractIncomingMessage
from app.common.schemas.base import BaseSchema
from app.consumers.base import BaseConsumer
from app.resources.sse import RedisSSEManager

logger = logging.getLogger(__name__)


class SSEMessageSchema(BaseSchema):
    message: str


class SSEConsumer(BaseConsumer[SSEMessageSchema]):
    message_cls = SSEMessageSchema

    def __init__(self, *args, **kwargs):
        self.sse_manager = RedisSSEManager()
        super().__init__(*args, **kwargs)

    async def process_message(self, message: AbstractIncomingMessage) -> SSEMessageSchema:
        parsed_message = await super().process_message(message)
        logger.info(f"Message: {message.body}.")
        await self.sse_manager.send_message(parsed_message.model_dump_json())
        return parsed_message

    async def setup(self):
        await super().setup()
        await self.sse_manager.setup()

    async def shutdown(self):
        """Закрываем Redis соединение при завершении"""
        await self.sse_manager.shutdown()
        await super().shutdown()
