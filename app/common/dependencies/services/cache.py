from typing import Annotated

from app.common.dependencies.db.redis import RedisConnectionDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.services.base import BaseServiceError
from app.services.cache import CacheService
from fastapi import Depends
from fastapi.requests import Request


def get_cache_service(request: Request, connection: RedisConnectionDep):
    try:
        return CacheService(request=request, connection=connection)
    except BaseServiceError:
        raise BaseApiError


CacheServiceDep = Annotated[CacheService, Depends(get_cache_service)]
