import time

from app.common.logger import logger
from app.common.schemas.query_history import QueryHistoryBaseSchema
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
    app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET_KEY)  # pycharm подчеркивает

    @app.middleware("http")
    async def compute_process_time(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        try:
            # Ошибки в rabbitmq не должны класть весь API
            q = QueryHistoryBaseSchema(
                method=request.method,
                url_path=request.url.path,
                query_string=request.url.query,
                status_code=response.status_code,
                process_time=process_time,
            )
            await request.app.history_publisher.publish(message=q)
        except Exception as e:
            logger.error(e)

        return response
