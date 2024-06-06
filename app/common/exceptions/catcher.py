import asyncio
from contextlib import contextmanager
from functools import wraps
from typing import Callable, Type


def catch_exception(base_error: Type[Exception], description: str = "exception", verbose=True) -> Callable:
    """Декоратор, который ловит все исключения в методе класса"""

    def wrapper(method: Callable) -> Callable:
        @contextmanager
        def catching(self, *args, **kwargs):
            try:
                yield
            except Exception as ex:
                # TODO: Эти исключения уже ловились. Надо подумать, как с ними работать
                #  + ConnectionRefusedError (когда бд отключена)
                # except MultipleResultsFound as e:
                #     # Если хотим скаляр (одну строку), а под такие критерии подходит несколько
                #     raise BaseRepoError(e, self.model_name, kwargs)
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

                model_name = self.__class__.__name__
                exception_name = ex.__class__.__name__
                message = f"{exception_name}: \n{ex}\n{description} from {model_name}"
                message = "\n\t".join(message.split("\n"))
                if verbose:
                    print(f"{message}")  # TODO: весь трейс в логи logger, sentry etc
                raise UnitingException(message) from ex

        @wraps(method)  # TODO: узнать, зачем это
        def executor(self, *args, **kwargs):
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
