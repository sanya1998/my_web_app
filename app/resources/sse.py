import asyncio
import logging
import random
from asyncio import CancelledError
from enum import Enum
from time import time
from typing import Set

from app.config.common import settings
from app.resources.redis_ import BasePubsubListener
from starlette.requests import Request

logger = logging.getLogger(__name__)


class QueueFullStrategy(Enum):
    REPLACE_OLDEST = "replace_oldest"
    SKIP_MESSAGE = "skip_message"
    WAIT_TIMEOUT = "wait_with_timeout"


class SSEManager:
    def __init__(self):
        self._queues: Set[asyncio.Queue] = set()
        self._lock = asyncio.Lock()

    @staticmethod
    async def add_message_to_queue(
        message: str,
        queue: asyncio.Queue,
        strategy: QueueFullStrategy = QueueFullStrategy.REPLACE_OLDEST,
        timeout: float = 1.0,
    ):
        if not queue.full():
            await queue.put(message)
        elif strategy == QueueFullStrategy.SKIP_MESSAGE:
            pass
        elif strategy == QueueFullStrategy.REPLACE_OLDEST:
            try:
                await queue.get()
            except asyncio.QueueEmpty:
                pass
            finally:
                await queue.put(message)
        elif strategy == QueueFullStrategy.WAIT_TIMEOUT:
            try:
                await asyncio.wait_for(queue.put(message), timeout=timeout)
            except asyncio.TimeoutError:
                pass

    async def _broadcast_to_queues(self, message: str, batch_size: int = 100):
        queues = await self._get_all_queues()
        if not queues:
            return
        for i in range(0, len(queues), batch_size):
            batch = queues[i : i + batch_size]
            tasks = [asyncio.create_task(self.add_message_to_queue(message, queue)) for queue in batch]
            await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(f"📨 Message was sent to {len(queues)} clients.")

    async def messages_listener(self, request: Request):
        client_queue = asyncio.Queue(maxsize=settings.SSE_QUEUE_SIZE)
        await self._add_queue(client_queue)
        logger.info(f"👥 New SSE client is connected. Total: {await self._get_queue_count()}.")
        try:
            queue_timeout = settings.SSE_QUEUE_TIMEOUT + random.uniform(0, 1.0)
            reconnection_time = time() + settings.SSE_MAX_CONNECTION_TIME + random.uniform(0, 30)
            while not await request.is_disconnected():
                if time() > reconnection_time:
                    logger.info("⏰ SSE client will be reconnected by timeout.")
                    break
                try:
                    message = await asyncio.wait_for(client_queue.get(), queue_timeout)
                    yield f"data: {message}\n"
                except asyncio.TimeoutError:
                    continue
        except CancelledError:
            logger.info("🚶 Stream was cancelled. SSE client will be disconnected.")
        finally:
            await self._remove_queue(client_queue)
            logger.info(f"👋 SSE client was disconnected. Total: {await self._get_queue_count()}.")

    async def _add_queue(self, queue: asyncio.Queue):
        async with self._lock:
            self._queues.add(queue)

    async def _remove_queue(self, queue: asyncio.Queue):
        async with self._lock:
            self._queues.discard(queue)

    async def _get_all_queues(self):
        async with self._lock:
            return list(self._queues)

    async def _get_queue_count(self):
        async with self._lock:
            return len(self._queues)


class SSEPubsubListener(SSEManager, BasePubsubListener):
    """
    send_message: Anywhere PubsubSender sends message to Redis pubsub channel.
    _pubsub_listener: All instances of BasePubsubListener receive messages from Redis pubsub channel.
    _process_message: All instances of BasePubsubListener process one message.
    _broadcast_to_queues: All instances of SSEManager writes one message to their queues.
    messages_listener: SSEManager reads messages from queue and generates sse-message for client.
    """

    def __init__(self, channel_name: str):
        SSEManager.__init__(self)
        BasePubsubListener.__init__(self, channel_name)

    async def _process_message(self, message: str):
        await self._broadcast_to_queues(message)
