from app.common.exceptions.api.base import BaseApiError
from starlette import status


class ForbiddenApiError(BaseApiError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Forbidden"
