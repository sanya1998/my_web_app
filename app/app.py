from contextlib import asynccontextmanager

from app.api import api_router
from app.cms.cms import add_cms
from app.config.common import settings
from app.exceptions.handlers import add_exceptions
from app.middlewares.middlewares import add_middlewares
from app.resources.hawk_ import add_hawk_fastapi
from app.resources.prometheus_ import add_prometheus
from app.resources.rmq.base_publisher import BasePublisher
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app_: FastAPI):
    # TODO: поле app_.history_publisher функционирует, но нет подсказок IDE для app_.history_publisher
    async with BasePublisher(settings.HISTORY_ROUTING_KEY, settings.HISTORY_EXCHANGE_NAME) as app_.history_publisher:
        yield


app = FastAPI(
    lifespan=lifespan,
    debug=settings.DEBUG,
    title=settings.APPLICATION_NAME,
    description=settings.APPLICATION_DESCRIPTION,
    swagger_ui_parameters=settings.SWAGGER_UI_PARAMETERS,
    default_response_class=ORJSONResponse,
)
app.include_router(api_router)
app.mount(path="/static", app=StaticFiles(directory="static/"), name="static")  # TODO: envs

add_exceptions(app)
add_middlewares(app)
add_cms(app)
add_hawk_fastapi(app)
add_prometheus(app)
