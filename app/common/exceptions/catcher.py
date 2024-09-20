import asyncio
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Type


def catch_exception(base_error: Type[Exception], description: str = "exception", verbose=True) -> Callable:
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
                    """
                    `raise UnitingException` можно поймать с помощью `except base_error`,
                    ex.__class__ содержит информацию об ошибке,
                    method_args, method_kwargs - входные данные.
                    """

                    method_args = args
                    method_kwargs = kwargs

                method_name = method.__name__
                model_name = self.__class__.__name__
                exception_name = ex.__class__.__name__
                message = f"{exception_name}: \n{ex}\n{description}. Model: {model_name}. Method: {method_name}."
                message = "\n\t".join(message.split("\n"))  # TODO: иногда тут неполная инфа, например SQLAlchemyError
                if verbose:
                    print(f"{message}")  # TODO: весь трейс в логи logger, sentry etc
                raise UnitingException(message) from ex

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
