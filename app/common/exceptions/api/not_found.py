from app.common.exceptions.api.base import BaseApiError


class ApiNotFoundError(BaseApiError):
    status_code = 404
