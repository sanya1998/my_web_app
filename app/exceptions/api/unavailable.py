from app.exceptions.api.base import BaseApiError
from app.exceptions.api.schemas.detail import DetailSchema
from starlette import status


class UnavailableApiError(BaseApiError):
    status_code = status.HTTP_409_CONFLICT
    detail = DetailSchema(detail="Unavailable")
