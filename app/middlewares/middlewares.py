import time

from app.common.schemas.query_history import QueryHistoryBaseSchema
from app.config.common import settings
from app.repositories.query_history import QueryHistoryRepo
from app.resources.postgres import async_session
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

    @app.middleware("http")
    async def compute_process_time(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        # TODO: отправлять сообщение в кролик с информацией, сколько длился запрос, а он пусть пишет в бд
        # TODO: обрабатывать ошибку, если запрос был дольше 100 секунд (бд не примет его)
        q = QueryHistoryBaseSchema(
            method=request.method,
            url_path=request.url.path,
            query_string=request.url.query,
            status_code=response.status_code,
            process_time=process_time,
        )
        async with async_session() as session:
            r = QueryHistoryRepo(session=session)
            await r.create(q)

        return response
