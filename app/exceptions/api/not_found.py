from app.exceptions.api.base import BaseApiError
from app.exceptions.api.schemas.detail import DetailSchema
from starlette import status


class NotFoundApiError(BaseApiError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = DetailSchema(detail="Not found")
