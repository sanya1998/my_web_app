from typing import Annotated, AsyncIterator

from aioredis.client import Redis
from app.resources.redis import redis
from fastapi import Depends


async def get_redis_session() -> AsyncIterator[Redis]:
    async with redis.client() as conn:
        yield conn


RedisConnectionDep = Annotated[Redis, Depends(get_redis_session)]
