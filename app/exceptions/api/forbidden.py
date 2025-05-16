from app.exceptions.api.base import BaseApiError
from app.exceptions.api.schemas.detail import DetailSchema
from starlette import status


class ForbiddenApiError(BaseApiError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = DetailSchema(detail="Forbidden")
