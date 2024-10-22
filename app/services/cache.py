from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, Optional, Tuple

from redis.asyncio.client import Redis

from app.common.constants.cache import CacheObjectEnum, CacheListingEnum
from app.config.main import settings
from app.services.base import BaseService
from fastapi.requests import Request
from fastapi.responses import Response


class CacheService(BaseService):
    """
    Сервис записывает и очищает кеш для get-ручки получения одного объекта и для get-ручки получения списка объектов.

    Требования:
        - Get-ручка получения одного объекта: '/api/v{version}/{objects}/{object_id}', e.g.:
            - '/api/v1/hotels/16'
        - Get-ручка получения списка объектов: '/api/v{version}/{objects}/', e.g.:
            - '/api/v1/hotels/'
        TODO: get '/api/v1/bookings/for_current_user' работать будет некорректно

    Ключ в хранилище:
        - Для одного объекта: {objects}{object_id}, e.g.:
            - 'hotels16'
        - Для списка объектов: {objects}{cls.delimiter}{query_params}, e.g.:
            - 'hotels:[('limit', '10'), ('offset', '0'), ('ordering', 'id')]'

    Может очистить кеш после выполнения ручек:
        - '/api/v{version}/{objects}/{object_id}/*', e.g.:
            - put '/api/v1/hotels/16/for_moderator'
            - delete '/api/v1/hotels/16/for_moderator'
        - '/api/v{version}/{objects}/*', e.g.:
            - post '/api/v1/hotels/for_moderator'
    """
    delimiter: str = ":"

    @BaseService.catcher
    def __init__(self, request: Request, connection: Redis):
        super().__init__()
        self.request = request
        self.conn = connection

    @classmethod
    @BaseService.catcher
    def request_key_builder(
            cls,
            func: Callable[..., Any],
            namespace: str = "",
            *,
            request: Optional[Request] = None,
            response: Optional[Response] = None,
            args: Tuple[Any, ...],
            kwargs: Dict[str, Any],
    ) -> str:
        object_type = namespace[1:]  # Убрать двоеточие в начале
        base_key = f"{object_type}{cls.delimiter}"
        if CacheObjectEnum.contains(object_type):
            object_id = request.path_params.get("object_id")
            # Кеш для get-ручки получения одного объекта по id
            base_key = f"{base_key}{object_id}"
        elif CacheListingEnum.contains(object_type):
            # Кеш для get-ручки получения списка объектов по фильтрам
            # path_params = repr(sorted(request.path_params.items()))
            query_params = repr(sorted(request.query_params.multi_items()))
            base_key = f"{base_key}{query_params}"

        # TODO: не пострадает ли безопасность в плане ролей. Вперед авторизация или кеш?
        result = f"{base_key}{cls.delimiter}"
        return result

    @BaseService.catcher
    async def delete_objects_cache(self, objects_name: str):
        # Очистить кеш для листингов объектов
        await self.delete_cache_by_pattern(pattern=f"{objects_name}{self.delimiter}*")

    @BaseService.catcher
    async def delete_object_cache(self, object_name: str, object_id: int):
        # Очистить кеш для объекта
        await self.delete_cache_by_pattern(pattern=f"{object_name}{self.delimiter}{object_id}*")

    @BaseService.catcher
    async def delete_cache_by_pattern(self, pattern: str):
        async for key in self.conn.scan_iter(pattern):
            await self.delete_cache_by_key(key)

    @BaseService.catcher
    async def delete_cache_by_key(self, key: str):
        # Удаляет из бд (из кеша памяти), но оставляет в кеше диска, то есть в той же вкладке кеш останется.
        # Но в том, что это является очисткой кеша, можно убедиться, открыв инкогнито-вкладку.
        await self.conn.delete(key)
