from contextlib import asynccontextmanager

from app.api import api_router
from app.config.main import settings
from app.middlewares import add_all_middlewares
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


class Application(FastAPI):
    def setup(self) -> None:
        self.include_router(api_router)
        self.mount(path="/static", app=StaticFiles(directory="static/"), name="static")
        super().setup()


@asynccontextmanager
async def lifespan(application: Application):
    # application.state.resource1 = Resource1().start()
    yield
    # application.state.resource1.close()


app = Application(
    lifespan=lifespan,
    debug=settings.DEBUG,
    title=settings.APPLICATION_NAME,
    description=settings.APPLICATION_DESCRIPTION,
    swagger_ui_parameters=settings.SWAGGER_UI_PARAMETERS,
)

add_all_middlewares(app)
