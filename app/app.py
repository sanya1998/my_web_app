from fastapi import FastAPI

from app.api import api_router
from app.config import settings

app = FastAPI(
    debug=settings.DEBUG,
    title=settings.APPLICATION_NAME,
    description=settings.APPLICATION_DESCRIPTION,
    swagger_ui_parameters=settings.SWAGGER_UI_PARAMETERS,
)

app.include_router(api_router)
