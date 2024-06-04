from functools import wraps
from typing import Callable

from app.common.exceptions.services.base import BaseServiceError


class BaseService:
    def __init__(self, *args, **kwargs) -> None:
        self.model_name = self.__class__.__name__

    @staticmethod
    def catch_exception(method: Callable) -> Callable:  # TODO: подумать, как бы убрать дублирование. мб обернуть init ?
        @wraps(method)
        async def wrapper(self, *args, **kwargs):
            try:
                return await method(self, *args, **kwargs)
            except Exception as ex:

                class UnitingException(ex.__class__, BaseServiceError):
                    method_args = args
                    method_kwargs = kwargs

                message = f"{ex.__class__.__name__}: {ex}.\nService exception from {self.model_name}."
                print(message)  # TODO: весь трейс в логи logger, sentry etc
                raise UnitingException(message) from ex

        return wrapper
