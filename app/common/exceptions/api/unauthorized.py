from app.common.exceptions.api.base import BaseApiError
from starlette import status


class UnauthorizedApiError(BaseApiError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "User is unauthorized"


class MissingTokenApiError(UnauthorizedApiError):
    detail = "Token is missing"


class InvalidTokenApiError(UnauthorizedApiError):
    detail = "Invalid token error"


class ExpiredSignatureApiError(InvalidTokenApiError):
    detail = "Token has expired"


class MissingRequiredClaimApiError(InvalidTokenApiError):
    detail = "Required fields are not contained"
