from typing import Annotated, Dict

from app.common.logger import logger
from app.exceptions.api import BaseApiError
from app.exceptions.api.schemas.detail import DetailSchema
from app.exceptions.repositories import BaseRepoError
from app.exceptions.services import BaseServiceError
from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException


class ErrorResponseSchema(BaseModel):
    """Модель ответа при BaseApiError (и его потомках). Значения по умолчанию используются для неожидаемых исключений"""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    content: Annotated[DetailSchema | None, Field(alias="detail")] = DetailSchema()
    headers: Dict[str, str] | None = None


def common_preparing_of_handlers(request: Request, exc: Exception) -> ORJSONResponse:
    unexpected_error_response = ORJSONResponse(**ErrorResponseSchema().model_dump())
    logger.error("Error (%s %s) %s", request.method, request.url, exc)
    return unexpected_error_response


def add_exceptions(app: FastAPI):
    @app.exception_handler(BaseRepoError)
    async def base_repo_exception_handler(request: Request, exc: BaseRepoError):
        """Необрабатываемые исключения из репозиториев, вызванные BaseRepoError и его потомками"""
        return common_preparing_of_handlers(request, exc)

    @app.exception_handler(BaseServiceError)
    async def base_service_exception_handler(request: Request, exc: BaseServiceError):
        """Необрабатываемые исключения из сервисов, вызванные BaseServiceError и его потомками"""
        return common_preparing_of_handlers(request, exc)

    @app.exception_handler(RequestValidationError)
    async def custom_validation_exception_handler(request: Request, exc: RequestValidationError):
        """Любое исключение валидации можно переопределить здесь"""
        logger.warning("Error (%s %s) %s", request.method, request.url, exc)
        return await request_validation_exception_handler(request, exc)

    @app.exception_handler(BaseApiError)
    def base_api_exception_handler(request: Request, exc: BaseApiError):
        """Исключения api, вызванные BaseApiError и его потомками"""
        error = ErrorResponseSchema.model_validate(exc, from_attributes=True)
        return ORJSONResponse(**error.model_dump())

    @app.exception_handler(StarletteHTTPException)
    async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Любое необрабатываемое исключение api, не родственное BaseApiError"""
        if 400 <= exc.status_code < 500:
            logger.warning("Warning (%s %s) %s", request.method, request.url, exc)
        else:
            logger.error("Error (%s %s) %s", request.method, request.url, exc)
        return await http_exception_handler(request, exc)

    @app.exception_handler(Exception)
    async def common_exception_handler(request: Request, exc: Exception):
        """Все остальные необрабатываемые исключения"""
        return common_preparing_of_handlers(request, exc)
