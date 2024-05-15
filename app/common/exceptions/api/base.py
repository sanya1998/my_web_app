import json

from app.common.exceptions.repositories.base import BaseRepoError
from app.common.helpers.json import CustomEncoder
from fastapi import HTTPException


class BaseApiError(HTTPException):
    status_code = 500

    def __init__(self, e: BaseRepoError):
        self.model_name = e.model_name
        self.problem = e.problem
        self.detail = json.loads(json.dumps(e.detail, cls=CustomEncoder))

    def __str__(self):
        return f"{self.model_name} : {self.problem} : {self.detail}"
