import redis.asyncio as aioredis
from app.config.common import settings

pool = aioredis.ConnectionPool.from_url(url=settings.CACHE_URL, max_connections=settings.CACHE_MAX_CONNECTIONS)


def with_redis_client(func):
    """
    @with_redis_client
    async def func(arg, redis_client, kwarg=None):
        pass

    await func(1, kwarg=2)
    """

    async def wrapper(*args, **kwargs):
        redis_client = aioredis.Redis.from_pool(pool)
        try:
            return await func(*args, redis_client=redis_client, **kwargs)
        finally:
            await redis_client.aclose()

    return wrapper
