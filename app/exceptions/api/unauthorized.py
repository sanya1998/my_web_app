from app.exceptions.api.base import BaseApiError
from app.exceptions.api.schemas.detail import DetailSchema
from starlette import status


class UnauthorizedApiError(BaseApiError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = DetailSchema(detail="User is unauthorized")
    headers = {"WWW-Authenticate": "Bearer"}


class MissingTokenApiError(UnauthorizedApiError):
    detail = DetailSchema(detail="Token is missing")


class InvalidTokenApiError(UnauthorizedApiError):
    detail = DetailSchema(detail="Invalid token error")


class ExpiredSignatureApiError(InvalidTokenApiError):
    detail = DetailSchema(detail="Token has expired")


class MissingRequiredClaimApiError(InvalidTokenApiError):
    detail = DetailSchema(detail="Required fields are not contained")
