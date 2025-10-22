from contextlib import asynccontextmanager

from app.api import api_router
from app.cms.cms import add_cms
from app.config.common import settings
from app.exceptions.handlers import add_exceptions
from app.middlewares.middlewares import add_middlewares
from app.publishers.base import BasePublisher
from app.resources.hawk_ import add_hawk_fastapi
from app.resources.postgres import PostgresManager
from app.resources.prometheus_ import add_prometheus
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.datastructures import State


class App(FastAPI):
    state: State


@asynccontextmanager
async def lifespan(app_: App):
    async with (
        BasePublisher(settings.HISTORY_ROUTING_KEY, settings.HISTORY_EXCHANGE_NAME) as history_publisher,
        PostgresManager() as postgres_manager,
    ):
        app_.state.postgres_manager = postgres_manager
        app_.state.history_publisher = history_publisher

        await add_cms(app_, postgres_manager)

        yield


app = App(
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
add_hawk_fastapi(app)
add_prometheus(app)
