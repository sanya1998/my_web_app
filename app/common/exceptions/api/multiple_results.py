from app.common.exceptions.api.base import BaseApiError
from starlette import status


class MultipleResultsApiError(BaseApiError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Multiple results"
