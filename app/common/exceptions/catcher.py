import asyncio
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Type

from app.common.logger import logger


def catch_exception(base_error: Type[Exception], description: str = "Exception description", exc_info=True) -> Callable:
    """Декоратор, который позволяет ловить все исключения в методе с помощью 'except <base_error>'"""

    def wrapper(method: Callable) -> Callable:
        @contextmanager
        def catching(self, *args, **kwargs):
            try:
                yield
            except Exception as ex:
                # TODO: Эти исключения уже ловились. Надо подумать, как с ними работать
                # except InvalidRequestError as e:
                #     # Одно из пришедших полей отсутствует в таблице
                #     raise BaseRepoError(e, self.model_name, kwargs)
                # except CompileError as e:
                #     # Если при создании придет поле, которого нет в таблице. (по идее должно решиться SQLModel)
                #     raise BaseRepoError(e, self.model_name, kwargs)
                class UnitingException(ex.__class__, base_error):
                    pass

                if (exception_name := ex.__class__.__name__) != "UnitingException":
                    # TODO: check: иногда тут неполная инфа, например SQLAlchemyError, ValidationError
                    extra = {
                        "class": self.__class__.__name__,
                        "method": method.__name__,
                        "method_args": args,
                        "method_kwargs": kwargs,
                        "ex_class": exception_name,
                        "ex": ex,
                    }
                    # TODO: не всегда logger.error, иногда warning или info
                    # TODO: весь трейс в sentry, hawk
                    logger.error(description, extra=extra, exc_info=exc_info)

                # `raise UnitingException` можно поймать с помощью `except base_error`
                raise UnitingException from ex

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
