from app.common.exceptions.api.base import BaseApiError
from starlette import status


class UnavailableApiError(BaseApiError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Unavailable"
