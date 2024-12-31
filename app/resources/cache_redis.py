import redis.asyncio as aioredis
from app.config.main import settings

pool = aioredis.ConnectionPool.from_url(url=settings.REDIS_URL, max_connections=settings.REDIS_MAX_CONNECTIONS)


def with_redis_client(func):
    """
    @with_redis_client
    async def func(arg, redis_client, kwarg=None):
        pass

    await func(1, kwarg=2)
    """

    async def wrapper(*args, **kwargs):
        redis_client = aioredis.Redis.from_pool(pool)
        result = await func(*args, redis_client=redis_client, **kwargs)
        await redis_client.aclose()  # TODO: try: finally:
        return result

    return wrapper
