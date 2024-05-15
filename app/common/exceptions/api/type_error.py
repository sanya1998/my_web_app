from app.common.exceptions.api.base import BaseApiError


class ApiTypeError(BaseApiError):
    status_code = 500
