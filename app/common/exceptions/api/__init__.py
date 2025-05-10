from app.common.exceptions.api.already_exists import AlreadyExistsApiError
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.forbidden import ForbiddenApiError
from app.common.exceptions.api.multiple_results import MultipleResultsApiError
from app.common.exceptions.api.not_found import NotFoundApiError
from app.common.exceptions.api.unauthorized import (
    ExpiredSignatureApiError,
    InvalidTokenApiError,
    MissingRequiredClaimApiError,
    MissingTokenApiError,
    UnauthorizedApiError,
)
from app.common.exceptions.api.unavailable import UnavailableApiError
from app.common.exceptions.api.unprocessable_entity import UnprocessableEntityApiError
