from app.common.exceptions.api.base import BaseApiError
from fastapi import status


class AlreadyExistsApiError(BaseApiError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Already exists"
