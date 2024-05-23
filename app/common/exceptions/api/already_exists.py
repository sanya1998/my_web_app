from app.common.exceptions.api.base import BaseApiError


class AlreadyExistsError(BaseApiError):
    status_code = 409
