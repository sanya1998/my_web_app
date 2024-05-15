from app.common.exceptions.repositories.base import BaseNotFoundError, BaseTypeError


class BookingNotFoundError(BaseNotFoundError):
    pass


class BookingTypeError(BaseTypeError):
    pass
