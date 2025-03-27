from app.config.common import settings
from fastapi import FastAPI
from hawk_python_sdk import Hawk
from hawk_python_sdk.modules.fastapi import HawkFastapi


def check_hawk_token(func):
    def wrapper(*args, **kwargs):
        if not settings.HAWK_TOKEN:
            return
        return func(*args, **kwargs)

    return wrapper


@check_hawk_token
def init_hawk():
    Hawk(settings.HAWK_TOKEN)


@check_hawk_token
def add_hawk_fastapi(app: FastAPI):
    # Ловит ошибки внутри эндпоинта, но не ловит ошибки в Depends (например, игнорит отсутствие подключения к бд)
    HawkFastapi({"app_instance": app, "token": settings.HAWK_TOKEN})
