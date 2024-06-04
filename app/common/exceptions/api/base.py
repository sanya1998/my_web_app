# import json
#
# from app.common.exceptions.repositories.base import BaseRepoError
# from app.common.helpers.json import CustomEncoder
from fastapi import HTTPException, status


class BaseApiError(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)

    #     # TODO: нужно ли теперь это (в тч CustomEncoder)
    #     self.detail = json.loads(json.dumps(self.detail, cls=CustomEncoder))
