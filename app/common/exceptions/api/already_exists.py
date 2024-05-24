from app.common.exceptions.api.base import BaseApiError


class ApiAlreadyExistsError(BaseApiError):
    status_code = 409
    detail = "Already exists"
