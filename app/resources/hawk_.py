from app.common.constants.environments import Environments
from app.config.main import settings
from fastapi import FastAPI
from hawk_python_sdk import Hawk
from hawk_python_sdk.modules.fastapi import HawkFastapi


def init_hawk():
    Hawk(settings.HAWK_TOKEN)


def add_hawk_fastapi(app: FastAPI):
    if settings.ENVIRONMENT == Environments.TEST:
        return
    # Ловит ошибки внутри эндпоинта, но не ловит ошибки в Depends (например, игнорит отсутствие подключения к бд)
    HawkFastapi({"app_instance": app, "token": settings.HAWK_TOKEN})
