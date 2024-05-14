from contextlib import asynccontextmanager

from app.api import api_router
from app.config.main import settings
from fastapi import FastAPI


class Application(FastAPI):
    def init_routers(self) -> None:
        self.include_router(api_router)

    def setup(self) -> None:
        self.init_routers()

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
