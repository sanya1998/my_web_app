from app.common.exceptions.catcher import catch_exception
from app.common.exceptions.services.already_exists import AlreadyExistsServiceError
from app.common.exceptions.services.base import BaseServiceError
from app.common.exceptions.services.not_found import NotFoundServiceError
from app.common.exceptions.services.unauthorized import (
    ExpiredSignatureServiceError,
    InvalidAlgorithmServiceError,
    InvalidTokenServiceError,
    MissingRequiredClaimServiceError,
    UnauthorizedServiceError,
)
from app.common.exceptions.services.unavailable import UnavailableServiceError


class BaseService:
    catcher = catch_exception(
        base_error=BaseServiceError,
        description="Service exception",
        warnings=[
            AlreadyExistsServiceError,
            NotFoundServiceError,
            UnauthorizedServiceError,
            UnavailableServiceError,
            MissingRequiredClaimServiceError,
            ExpiredSignatureServiceError,
            InvalidAlgorithmServiceError,
            InvalidTokenServiceError,
        ],
    )
