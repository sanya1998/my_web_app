from app.exceptions.services.base import BaseServiceError


class UnauthorizedServiceError(BaseServiceError):
    pass


class InvalidTokenServiceError(UnauthorizedServiceError):
    pass


class InvalidAlgorithmServiceError(InvalidTokenServiceError):
    pass


class ExpiredSignatureServiceError(InvalidTokenServiceError):
    pass


class MissingRequiredClaimServiceError(InvalidTokenServiceError):
    pass
