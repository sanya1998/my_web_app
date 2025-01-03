from app.common.exceptions.api.base import BaseApiError
from starlette import status


class UnprocessableEntityApiError(BaseApiError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Unprocessable Entity"
