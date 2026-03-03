import asyncio
import logging
import platform
from typing import Optional

import redis.asyncio as redis
from app.config.common import settings
from redis.asyncio import Redis

logger = logging.getLogger(__name__)

# TODO: посмотреть в тассбэке решение, которое удобно при полном падении редиса.
# TODO: два раза создается экземпляр в этом файле (redis.ConnectionPool.from_url и redis.from_url)
# max_connections=settings.REDIS_MAX_CONNECTIONS,
# client_name=platform.node(), # import platform
pool = redis.ConnectionPool.from_url(url=settings.CACHE_URL, max_connections=settings.REDIS_MAX_CONNECTIONS)


def with_redis_client(func):
    """
    @with_redis_client
    async def func(arg, redis_client, kwarg=None):
        pass

    await func(1, kwarg=2)
    """

    async def wrapper(*args, **kwargs):
        redis_client = redis.Redis.from_pool(pool)
        try:
            return await func(*args, redis_client=redis_client, **kwargs)
        finally:
            await redis_client.aclose()

    return wrapper


class BasePubsub:
    def __init__(self, channel_name: str):
        self.redis: Redis | None = None
        self.channel_name = channel_name

    async def setup(self):
        self.redis = redis.from_url(
            url=settings.REDIS_BASE_URL,
            decode_responses=True,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            health_check_interval=settings.REDIS_HEALTH_CHECK_INTERVAL,
            socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
            socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
            client_name=platform.node(),
        )

    async def __aenter__(self):
        await self.setup()
        return self

    async def shutdown(self):
        await self.redis.close()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.shutdown()


class PubsubSender(BasePubsub):
    """Use `send_message` to send one message in Redis Pubsub (For example, in your consumer)."""

    async def send_message(self, message: str):
        try:
            await self.redis.publish(self.channel_name, message)
            logger.debug(f"📨 Published to Redis: {message}")
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.error(f"🔌 Redis connection error: {e}.")


class BasePubsubListener(BasePubsub):
    """Use `messages_listener` to subscribe new client to all new messages (For example, in your api instance)."""

    def __init__(self, channel_name: str):
        super().__init__(channel_name)
        self._pubsub_task: Optional[asyncio.Task] = None

    async def setup(self):
        await super().setup()
        self._pubsub_task = asyncio.create_task(self._pubsub_listener())

    async def shutdown(self):
        self._pubsub_task.cancel()
        await super().shutdown()

    async def _process_message(self, message: str):
        pass

    async def _iter_listener(self, pubsub):
        try:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=settings.PUBSUB_TIMEOUT,
            )
            if message:
                await self._process_message(message["data"])
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.warning(f"⚠️ Redis is disconnected: {e}. Attempt of reconnecting will be after pause.")
            await asyncio.sleep(settings.REDIS_RECONNECT_INTERVAL)

    async def _pubsub_listener(self):
        try:
            async with self.redis.pubsub() as pubsub:
                await pubsub.subscribe(self.channel_name)
                while True:
                    await self._iter_listener(pubsub)
        except asyncio.CancelledError:
            logger.debug("🔔 PubSub listener cancelled.")
