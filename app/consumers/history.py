from app.common.logger import logger
from app.common.schemas.query_history import QueryHistoryBaseSchema
from app.consumers.base import BaseConsumer
from app.repositories.query_history import QueryHistoryRepo
from app.resources.postgres import PostgresManager


class HistoryConsumer(BaseConsumer[QueryHistoryBaseSchema]):
    message_cls = QueryHistoryBaseSchema

    def __init__(self, queue_name: str = "", **kwargs):
        self.postgres_manager = PostgresManager()
        super().__init__(queue_name=queue_name, **kwargs)

    async def shutdown(self):
        await super().shutdown()
        await self.postgres_manager.shutdown()

    async def process_message(self, message):
        message: QueryHistoryBaseSchema = await super().process_message(message)
        logger.info(f"Message: {message}")
        async with self.postgres_manager.session_factory() as session:
            r = QueryHistoryRepo(session=session)
            await r.create(message)
