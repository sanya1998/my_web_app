import asyncio
from contextlib import contextmanager
from functools import wraps
from typing import Callable

from app.common.exceptions.services.base import BaseServiceError


class BaseService:
    @staticmethod
    def catch_exception(method: Callable) -> Callable:
        @contextmanager
        def wrapping_logic(self, *args, **kwargs):
            try:
                yield
            except Exception as ex:

                class UnitingException(ex.__class__, BaseServiceError):
                    method_args = args
                    method_kwargs = kwargs

                message = f"{ex.__class__.__name__}: {ex}.\nService exception from {self.model_name}."
                print(message)  # TODO: весь трейс в логи logger, sentry etc
                raise UnitingException(message) from ex

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            if asyncio.iscoroutinefunction(method):

                async def async_wrapper():
                    with wrapping_logic(self, *args, **kwargs):
                        return await method(self, *args, **kwargs)

                return async_wrapper()
            else:
                with wrapping_logic(self, *args, **kwargs):
                    return method(self, *args, **kwargs)

        return wrapper

    @catch_exception
    def __init__(self, *args, **kwargs) -> None:
        self.model_name = self.__class__.__name__
