from app.common.exceptions.api.base import BaseApiError
from starlette import status


class NotFoundApiError(BaseApiError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Not found"
