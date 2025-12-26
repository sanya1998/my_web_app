from contextlib import asynccontextmanager

from app.api import api_router
from app.cms.cms import add_cms
from app.config.common import settings
from app.consumers.sse import SSEConsumer
from app.exceptions.handlers import add_exceptions
from app.middlewares.middlewares import add_middlewares
from app.publishers.base import BasePublisher
from app.resources.hawk_ import add_hawk_fastapi
from app.resources.postgres import PostgresManager
from app.resources.prometheus_ import add_prometheus
from app.resources.sse import SSEPubsubListener
from es.clients.pydantic_ import PydanticESClient
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.datastructures import State


class App(FastAPI):
    state: State


@asynccontextmanager
async def lifespan(app_: App):
    async with (
        SSEPubsubListener(channel_name=settings.PUBSUB_SSE_CHANNEL) as sse_pubsub,
        SSEConsumer(settings.SSE_QUEUE_NAME) as sse_consumer,
        BasePublisher(settings.SSE_ROUTING_KEY, settings.SSE_EXCHANGE_NAME) as publisher_of_new_sse_messages,
        BasePublisher(settings.HISTORY_ROUTING_KEY, settings.HISTORY_EXCHANGE_NAME) as history_publisher,
        PostgresManager() as postgres_manager,
        PydanticESClient(hosts=settings.ES_HOSTS, default_alias=settings.ES_PRODUCTS_BASE_ALIAS) as es_client,
    ):
        app_.state.sse_pubsub = sse_pubsub
        app_.state.sse_consumer = sse_consumer
        await app_.state.sse_consumer.consume()
        app_.state.publisher_of_new_sse_messages = publisher_of_new_sse_messages
        app_.state.postgres_manager = postgres_manager
        app_.state.history_publisher = history_publisher
        app_.state.es_client = es_client

        await add_cms(app_, postgres_manager)

        yield


app = App(
    lifespan=lifespan,
    debug=settings.DEBUG,
    version=settings.RELEASE_VERSION,
    title=settings.APPLICATION_NAME,
    description=settings.APPLICATION_DESCRIPTION,
    swagger_ui_parameters=settings.SWAGGER_UI_PARAMETERS,
    default_response_class=ORJSONResponse,
)
app.include_router(api_router)
app.mount(path=settings.STATIC_PATH, app=StaticFiles(directory=settings.STATIC_DIRECTORY), name=settings.STATIC_NAME)

add_exceptions(app)
add_middlewares(app)
add_hawk_fastapi(app)
add_prometheus(app)
