from contextlib import asynccontextmanager

from app.admin.admin import add_admin
from app.api import api_router
from app.config.common import settings
from app.middlewares.middlewares import add_middlewares
from app.resources.hawk_ import add_hawk_fastapi
from app.resources.prometheus_ import add_prometheus
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app_: FastAPI):
    yield


app = FastAPI(
    lifespan=lifespan,
    debug=settings.DEBUG,
    title=settings.APPLICATION_NAME,
    description=settings.APPLICATION_DESCRIPTION,
    swagger_ui_parameters=settings.SWAGGER_UI_PARAMETERS,
)
app.include_router(api_router)
app.mount(path="/static", app=StaticFiles(directory="static/"), name="static")  # TODO: envs

add_middlewares(app)
add_admin(app)
add_hawk_fastapi(app)
add_prometheus(app)
