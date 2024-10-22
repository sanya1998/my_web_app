from contextlib import asynccontextmanager

from app.api import api_router
from app.config.main import settings
from app.middlewares import add_all_middlewares
from app.resources.redis import prepare_redis_cache
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


class Application(FastAPI):
    def setup(self) -> None:
        self.include_router(api_router)
        self.mount(path="/static", app=StaticFiles(directory="static/"), name="static")
        super().setup()


@asynccontextmanager
async def lifespan(application: Application):
    prepare_redis_cache()

    yield


app = Application(
    lifespan=lifespan,
    debug=settings.DEBUG,
    title=settings.APPLICATION_NAME,
    description=settings.APPLICATION_DESCRIPTION,
    swagger_ui_parameters=settings.SWAGGER_UI_PARAMETERS,
)

add_all_middlewares(app)
