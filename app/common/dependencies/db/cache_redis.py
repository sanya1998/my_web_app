from typing import Annotated

from app.resources.cache_redis import get_redis_client
from fastapi import Depends
from redis.asyncio import Redis


# TODO: не используется, но, возможно, пригодится
async def get_client() -> Redis:
    return await get_redis_client()


RedisClientDep = Annotated[Redis, Depends(get_client)]
