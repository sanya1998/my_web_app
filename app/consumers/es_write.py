from typing import Any, Dict, List

from app.common.helpers.base_enum import BaseEnum
from app.common.logger import logger
from app.common.schemas.base import BaseSchema
from app.config.common import settings
from app.consumers.base import BaseConsumer
from es.clients.base import BaseESClient
from pydantic import Field


class ESMethod(BaseEnum):
    CREATE = "create"
    UPDATE = "update"


class Message(BaseSchema):
    method: ESMethod
    args: List[Any] = Field(default_factory=list)
    kwargs: Dict[str, Any] = Field(default_factory=dict)


class ESWriteConsumer(BaseConsumer[Message]):
    # TODO: зачем нужен Generic[MessageClass] в родителе, если все равно делается это:
    message_cls = Message

    def __init__(self, queue_name: str = "", use_write_alias: bool = False, **kwargs):
        self.es_client: BaseESClient = BaseESClient(
            hosts=settings.ES_HOSTS, base_alias=settings.ES_PRODUCTS_BASE_ALIAS, use_write_alias=use_write_alias
        )
        super().__init__(queue_name=queue_name, **kwargs)

    async def shutdown(self):
        await super().shutdown()
        await self.es_client.close()

    async def process_message(self, message):
        message: Message = await super().process_message(message)
        logger.info(f"Method: {message.method}")
        await getattr(self.es_client, message.method)(*message.args, **message.kwargs)
