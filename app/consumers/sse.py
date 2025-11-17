import logging

from aio_pika.abc import AbstractIncomingMessage
from app.common.schemas.base import BaseSchema
from app.config.common import settings
from app.consumers.base import BaseConsumer
from app.resources.redis_ import PubsubSender

logger = logging.getLogger(__name__)


class SSEMessageSchema(BaseSchema):
    message: str


class SSEConsumer(BaseConsumer[SSEMessageSchema]):
    message_cls = SSEMessageSchema

    def __init__(self, *args, **kwargs):
        self.pubsub_sender = PubsubSender(channel_name=settings.PUBSUB_SSE_CHANNEL)
        super().__init__(*args, **kwargs)

    async def process_message(self, message: AbstractIncomingMessage) -> SSEMessageSchema:
        parsed_message = await super().process_message(message)
        logger.info(f"Message: {message.body}.")
        await self.pubsub_sender.send_message(parsed_message.model_dump_json())
        return parsed_message

    async def setup(self):
        await self.pubsub_sender.setup()
        await super().setup()

    async def shutdown(self):
        await super().shutdown()
        await self.pubsub_sender.shutdown()
