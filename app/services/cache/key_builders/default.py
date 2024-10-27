from typing import Callable

delimiter = ":"


def build_key_default(func: Callable, *args, **kwargs) -> str:
    key = f"{delimiter}".join([func.__name__, repr(args), repr(sorted(kwargs.items()))])
    return key
