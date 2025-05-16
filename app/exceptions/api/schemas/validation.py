from typing import List

from pydantic import BaseModel


class ValidationErrorSchema(BaseModel):
    loc: List
    input: List | str
    msg: str | None = None
    type: str | None = None
