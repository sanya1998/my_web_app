from app.common.exceptions.api.base import BaseApiError
from fastapi import status


class NotFoundApiError(BaseApiError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Not found"
