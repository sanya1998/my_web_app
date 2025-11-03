import logging

from aio_pika.abc import AbstractIncomingMessage
from app.common.schemas.base import BaseSchema
from app.consumers.base import BaseConsumer
from app.resources.sse import SSEManager

logger = logging.getLogger(__name__)


class SSEMessageSchema(BaseSchema):
    message: str


class SSEConsumer(BaseConsumer[SSEMessageSchema]):
    message_cls = SSEMessageSchema

    def __init__(self, *args, **kwargs):
        self.sse_manager = SSEManager()
        super().__init__(*args, **kwargs)

    async def process_message(self, message: AbstractIncomingMessage) -> SSEMessageSchema:
        parsed_message = await super().process_message(message)
        logger.info(f"Message: {message.body}.")
        await self.sse_manager.send_message(parsed_message.message)
        return parsed_message
