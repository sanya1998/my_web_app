import typing

from fastapi.routing import APIRouter
from fastapi.types import DecoratedCallable

DEFAULT_VERSION = "v1"
VERSION_PROPERTY = "version"


class VersionedAPIRouter(APIRouter):
    def __init__(self, *args, is_root_router: bool = False, **kwargs):
        self.is_root_router = is_root_router
        super().__init__(*args, **kwargs)

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
        # Если используется не VersionedAPIRouter, а например fastapi.APIRouter, то у endpoint не будет указана версия
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
