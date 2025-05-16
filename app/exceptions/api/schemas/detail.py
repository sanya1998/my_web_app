from typing import Any

from pydantic import BaseModel


class DetailSchema(BaseModel):
    detail: Any = "Something went wrong"
