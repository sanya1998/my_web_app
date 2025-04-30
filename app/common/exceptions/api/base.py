from fastapi import HTTPException, status


class BaseApiError(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = None

    def __init__(self, status_code=None, detail=None):
        super().__init__(
            status_code=status_code if status_code else self.status_code, detail=detail if detail else self.detail
        )
