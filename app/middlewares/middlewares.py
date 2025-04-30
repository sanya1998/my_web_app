import time

from app.common.logger import logger
from app.config.common import settings
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request


def add_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOW_ORIGINS_REGEX,
        allow_credentials=settings.ALLOW_CREDENTIALS,
        allow_methods=settings.ALLOW_METHODS,
        allow_headers=settings.ALLOW_HEADERS,
    )
    app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET_KEY)

    # TODO: сделать единообразно
    # TODO: когда появится что-то со смыслом, этот можно будет убрать
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        # TODO: вместо логирования отправлять сообщение в кролик с информацией, сколько длился запрос,
        #  а он пусть пишет в бд
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info("Request handling time", extra={"process_time": round(process_time, 4)})
        return response
