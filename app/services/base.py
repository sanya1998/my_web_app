from app.exceptions.catcher import catch_exception
from app.exceptions.services import (
    AlreadyExistsServiceError,
    BaseServiceError,
    ExpiredSignatureServiceError,
    InvalidAlgorithmServiceError,
    InvalidTokenServiceError,
    MissingRequiredClaimServiceError,
    NotFoundServiceError,
    UnauthorizedServiceError,
    UnavailableServiceError,
)


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
