from app.exceptions.api.base import BaseApiError
from app.exceptions.api.schemas.detail import DetailSchema
from starlette import status


class MultipleResultsApiError(BaseApiError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = DetailSchema(detail="Multiple results")
