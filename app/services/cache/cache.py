import pickle
from functools import wraps
from typing import Callable, Dict, Tuple

from app.config.main import settings
from app.resources.cache_redis import with_redis_client
from app.services.base import BaseService
from app.services.cache.key_builders.default import build_key_default
from redis.asyncio import Redis


class CacheService(BaseService):
    @BaseService.catcher
    def __init__(
        self,
        *args,
        prefix_key: str = "",
        expire: int = settings.REDIS_CACHE_EXPIRE_DEFAULT,
        build_key: Callable[[Callable, Tuple, Dict], str] = build_key_default,
        build_key_for_clear: Callable[[Callable, Tuple, Dict], str] = build_key_default,
        build_key_pattern_for_clear: Callable[[Callable, Tuple, Dict], str] = build_key_default,
        **kwargs,
    ):
        """
        :param args:
        :param prefix_key: префикс ключа
        :param expire: время жизни кеша
        :param build_key: функция, возвращающая str и принимающая кешируемую функцию и ее входные данные
        :param kwargs:
        """
        super().__init__(*args, **kwargs)
        self.prefix_key = prefix_key
        self.expire = expire
        self.build_key = build_key
        self.build_key_for_clear = build_key_for_clear
        self.build_key_pattern_for_clear = build_key_pattern_for_clear

    @BaseService.catcher
    async def clear(
        self,
        prefix_key: str | None = None,
        clear_by_key: bool = False,
        build_key_for_clear: Callable = None,
        clear_by_pattern: bool = False,
        build_key_pattern_for_clear: Callable = None,
        **kwargs,
    ):
        """
        Очистить кеш
        :param prefix_key: Префикс ключа
        :param clear_by_key: True => build_key_for_clear(**kwargs), delete_cache_by_key(key)
        :param build_key_for_clear: Способ построения ключа для очистки
        :param clear_by_pattern: True => build_key_pattern_for_clear(**kwargs), delete_cache_by_pattern(pattern)
        :param build_key_pattern_for_clear: Способ построения паттерна для очистки
        :param kwargs: Данные, которые будут передаваться в функции построения ключа и построения паттерна ключа
        :return None:
        """
        prefix_key = prefix_key or self.prefix_key
        if clear_by_key:
            build_key_for_clear = build_key_for_clear or self.build_key_for_clear
            key = f"{prefix_key}{build_key_for_clear(**kwargs)}"
            await self.delete_cache_by_key(key=key)
        if clear_by_pattern:
            build_key_pattern_for_clear = build_key_pattern_for_clear or self.build_key_pattern_for_clear
            pattern = f"{prefix_key}{build_key_pattern_for_clear(**kwargs)}"
            await self.delete_cache_by_pattern(pattern=pattern)

    @BaseService.catcher
    @with_redis_client
    async def delete_cache_by_pattern(self, pattern: str, redis_client: Redis):
        # TODO: найти способ удаления по паттерну, чтобы выполнить одной командой
        async for key in redis_client.scan_iter(pattern):
            await self.delete_cache_by_key(key)

    @BaseService.catcher
    @with_redis_client
    async def delete_cache_by_key(self, key: str, redis_client: Redis):
        await redis_client.delete(key)

    @BaseService.catcher
    def caching(
        self,
        expire: int | None = None,
        prefix_key: str | None = None,
        build_key: Callable[[Callable, Tuple, Dict], str] = None,
    ):
        """
        Записать результат функции в кеш или считать результат функции, если он имеется в кеше
        :param expire: время жизни кеша
        :param prefix_key: префикс ключа
        :param build_key: функция построения ключа для записи и чтения
        :return:
        """

        def wrapper(func):
            @wraps(func)
            @with_redis_client
            async def inner(
                *args,
                redis_client: Redis,
                **kwargs,
            ):
                nonlocal expire, prefix_key, build_key
                expire = expire or self.expire
                prefix_key = prefix_key or self.prefix_key
                build_key = build_key or self.build_key

                key = f"{prefix_key}{build_key(func, *args, **kwargs)}"
                old_serialized_response = await redis_client.get(key)
                if old_serialized_response is not None:
                    return pickle.loads(old_serialized_response)
                new_response = await func(*args, **kwargs)
                serialized_response = pickle.dumps(new_response)
                await redis_client.set(key, serialized_response, ex=expire)
                return new_response

            return inner

        return wrapper
