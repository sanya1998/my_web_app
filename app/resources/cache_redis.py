from itertools import cycle

import redis.asyncio as aioredis
from app.config.main import settings


class RedisResource:
    """
    Документация redis говорит, что нужно выполнять `await client.aclose()`, если используется redis.asyncio
    TODO: не создается ли копия клиента при вызове `await RedisResource().new_client()` ?
    TODO: Не получилось реализовать так, чтоб один раз создать pool, а в дальнейшем создавать только сессии
    TODO: из-за ошибки при остановке приложения (pool уже закрыт, но снова пытается закрыть)
    """

    def __init__(self):
        self.client_generator = self._clients_cycle()

    @staticmethod
    async def _clients_cycle():
        while cycle:
            client = aioredis.Redis.from_url(url=settings.REDIS_URL)
            yield client
            await client.aclose()

    async def new_client(self):
        return await anext(self.client_generator)


get_redis_client = RedisResource().new_client
