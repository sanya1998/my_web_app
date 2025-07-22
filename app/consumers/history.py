from app.common.logger import logger
from app.repositories.query_history import QueryHistoryRepo
from app.resources.postgres import async_session
from app.resources.rmq.base_consumer import BaseConsumer


class HistoryConsumer(BaseConsumer):
    async def process_message(self, message):
        message = await super().process_message(message)
        logger.info(f"Message: {message}")

        async with async_session() as session:
            r = QueryHistoryRepo(session=session)
            await r.create(message)
