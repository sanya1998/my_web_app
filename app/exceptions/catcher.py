import asyncio
from contextlib import contextmanager
from functools import wraps
from typing import Callable, List, Type

from app.common.logger import logger


# TODO: сделать универсальным и для методов и для функций (убрать self), затем нацепить на with_redis_client
# TODO: мб в python есть проверка: это функция или метод?
def catch_exception(
    base_error: Type[Exception],
    description: str = "Exception description",
    exc_info=True,
    skips: List = None,
    infos: List = None,
    warnings: List = None,
) -> Callable:
    """Декоратор, который позволяет ловить все исключения в методе с помощью 'except <base_error>'"""

    def wrapper(method: Callable) -> Callable:
        @contextmanager
        def catching(self, *args, **kwargs):
            try:
                yield
            except Exception as ex:

                def raise_exception(ex_):
                    if ex_ is base_error:
                        raise
                    if isinstance(ex_, base_error):
                        raise ex_
                    raise base_error

                data = {
                    # TODO: не сработает type(self)?
                    "class": self.__class__.__name__,  # TODO: вроде args[0].__class__.__name__ if args else None,
                    "method": method.__name__,
                    "method_args": args,
                    "method_kwargs": kwargs,
                    "ex_class_name": ex.__class__.__name__,
                    "ex": ex,
                }
                if skips and ex.__class__ in skips:
                    raise_exception(ex)
                elif infos and ex.__class__ in infos:
                    logger.info(description, extra=data)
                elif warnings and ex.__class__ in warnings:
                    logger.warning(description, extra=data)
                else:
                    logger.error(description, extra=data, exc_info=exc_info)
                raise_exception(ex)

        @wraps(method)
        def executor(self, *args, **kwargs):
            # TODO: попробовать вынести with catching(self, *args, **kwargs):, чтобы не дублировать
            if asyncio.iscoroutinefunction(method):

                async def async_executor():
                    with catching(self, *args, **kwargs):
                        return await method(self, *args, **kwargs)

                return async_executor()
            else:
                with catching(self, *args, **kwargs):
                    return method(self, *args, **kwargs)

        return executor

    return wrapper
