import asyncio
import logging
from typing import Optional, Set

import redis.asyncio as redis
from app.config.common import settings
from starlette.requests import Request

logger = logging.getLogger(__name__)


class RedisSSEManager:
    def __init__(self, channel_name: str = "sse_messages"):
        self.redis = redis.from_url(settings.REDIS_BASE_URL, decode_responses=True)
        self.channel = channel_name
        self._queues: Set[asyncio.Queue] = set()
        self._pubsub_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()

    async def setup(self):
        """Явный запуск менеджера (вызывается один раз при старте приложения)"""
        if self._pubsub_task is None:
            self._pubsub_task = asyncio.create_task(self._pubsub_listener())

    async def send_message(self, message: str):
        try:
            await self.redis.publish(self.channel, message)
            logger.debug(f"📨 Published to Redis: {message}")
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.error(f"🔌 Redis connection error: {e}")

    async def event_generator(self, request: Request):
        client_queue = asyncio.Queue(maxsize=settings.SSE_QUEUE_SIZE)
        await self._add_queue(client_queue)
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    message = await asyncio.wait_for(client_queue.get(), timeout=settings.SSE_MESSAGE_WAITING_TIMEOUT)
                    yield f"data: {message}\n"
                except asyncio.TimeoutError:
                    continue
        finally:
            await self._remove_queue(client_queue)

    async def _pubsub_listener(self):
        async with self.redis.pubsub() as pubsub:
            await pubsub.subscribe(self.channel)
            try:
                while True:
                    message = await pubsub.get_message(
                        ignore_subscribe_messages=True,
                        timeout=settings.SSE_PUBSUB_TIMEOUT,
                    )
                    if message:
                        await self._broadcast_to_queues(message["data"])
            except asyncio.CancelledError:
                logger.debug("🔔 PubSub worker cancelled")

    async def _broadcast_to_queues(self, message: str, batch_size: int = 100):
        queues = await self._get_all_queues()
        if not queues:
            return
        for i in range(0, len(queues), batch_size):
            batch = queues[i : i + batch_size]
            tasks = [asyncio.create_task(queue.put(message)) for queue in batch]
            await asyncio.gather(*tasks, return_exceptions=True)
        logger.info(f"📨 Message sent to {len(queues)} clients")

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

    async def shutdown(self):
        if self._pubsub_task:
            self._pubsub_task.cancel()
        await self.redis.close()
