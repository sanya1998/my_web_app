# TODO: rename to responses.py
from typing import Generic, List, Optional, TypeVar, Union

from app.common.schemas.base import BaseSchema
from pydantic import BaseModel

ResponseType = TypeVar("ResponseType", bound=Union[BaseSchema, List[BaseSchema]])


class BaseResponse(BaseModel, Generic[ResponseType]):
    """
    Базовая модель для ответов api
    """

    content: Optional[ResponseType] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
