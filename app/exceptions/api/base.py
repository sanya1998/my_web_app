from typing import Any, Dict

from app.exceptions.api.schemas.detail import DetailSchema
from fastapi import HTTPException, status


class BaseApiError(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: DetailSchema = DetailSchema()
    headers: Dict[str, str] | None = None

    def __init__(self, status_code=None, detail: Any = None, headers=None):
        detail = detail if detail else self.detail
        super().__init__(
            status_code=status_code if status_code else self.status_code,
            detail=detail if isinstance(detail, DetailSchema) else DetailSchema(detail=detail),
            headers=headers if headers else self.headers,
        )
