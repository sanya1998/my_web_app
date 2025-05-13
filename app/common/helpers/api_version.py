import typing

from app.common.constants.paths import DEFAULT_VERSION
from app.common.logger import logger
from fastapi.routing import APIRouter
from fastapi.types import DecoratedCallable

VERSION_PROPERTY = "version"


class VersionedAPIRouter(APIRouter):
    def __init__(self, *args, is_root_router: bool = False, **kwargs):
        self.is_root_router = is_root_router
        try:
            super().__init__(*args, **kwargs)
        except (TypeError, AssertionError) as e:
            logger.error(f"Error while creating VersionedAPIRouter. {e}.")

    def api_route(
        self,
        path: str,
        **kwargs,
    ) -> typing.Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            # Навесить default-версию на endpoint, если она у него не указана
            if not hasattr(func, VERSION_PROPERTY):
                setattr(func, VERSION_PROPERTY, DEFAULT_VERSION)
            self.add_api_route(path, func, **kwargs)
            return func

        return decorator

    def add_api_route(self, path, endpoint, **kwargs):
        # Если используется fastapi.APIRouter, то в путь endpoint-а не добавится версия
        # Если это корневой VersionedAPIRouter, то добавляется версия в путь endpoint-а
        if self.is_root_router and (version := getattr(endpoint, VERSION_PROPERTY, None)):
            path = f"/{version}{path}"
        return super().add_api_route(path, endpoint, **kwargs)

    @staticmethod
    def set_api_version(
        version: str,
    ) -> typing.Callable[[DecoratedCallable], DecoratedCallable]:
        def decorator(func: DecoratedCallable) -> DecoratedCallable:
            setattr(func, VERSION_PROPERTY, version)
            return func

        return decorator
