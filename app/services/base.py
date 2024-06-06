from app.common.exceptions.catcher import catch_exception
from app.common.exceptions.services.base import BaseServiceError


class BaseService:
    catcher = catch_exception(base_error=BaseServiceError, description="service exception")

    @catcher
    def __init__(self, *args, **kwargs) -> None:
        self.model_name = self.__class__.__name__
