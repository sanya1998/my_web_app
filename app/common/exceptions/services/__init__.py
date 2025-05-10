from app.common.exceptions.services.already_exists import AlreadyExistsServiceError
from app.common.exceptions.services.base import BaseServiceError
from app.common.exceptions.services.forbidden import ForbiddenServiceError
from app.common.exceptions.services.multiple_results import MultipleResultsServiceError
from app.common.exceptions.services.not_found import NotFoundServiceError
from app.common.exceptions.services.unauthorized import (
    ExpiredSignatureServiceError,
    InvalidAlgorithmServiceError,
    InvalidTokenServiceError,
    MissingRequiredClaimServiceError,
    UnauthorizedServiceError,
)
from app.common.exceptions.services.unavailable import UnavailableServiceError
