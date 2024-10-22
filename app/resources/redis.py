import aioredis
from app.config.main import settings
from app.services.cache import CacheService
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

redis = aioredis.from_url(url=settings.REDIS_URL, max_connections=settings.REDIS_MAX_CONNECTIONS)


def prepare_redis_cache():
    FastAPICache.init(
        backend=RedisBackend(redis),
        expire=settings.REDIS_CACHE_EXPIRE,
        key_builder=CacheService.request_key_builder,  # TODO: pycharm подчеркивает
    )
