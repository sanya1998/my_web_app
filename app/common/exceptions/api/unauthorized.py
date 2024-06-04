from app.common.exceptions.api.base import BaseApiError
from fastapi import status


class UnauthorizedApiError(BaseApiError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "User is unauthorized"
