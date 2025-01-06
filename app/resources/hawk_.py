from app.config.main import settings

# TODO: когда скачается, то ипользовать from hawkcatcher.modules.fastapi import HawkFastapi
from app.resources.hawkcatchermodules.fastapi import HawkFastapi
from fastapi import FastAPI


def add_hawk(app: FastAPI):
    HawkFastapi({"app_instance": app, "token": settings.HAWK_TOKEN})
