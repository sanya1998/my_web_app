from typing import Annotated

from app.common.dependencies.filters.base import BaseFilterSchema
from fastapi import Depends


class UserFilterSchema(BaseFilterSchema):
    pass


UserFiltersDep = Annotated[UserFilterSchema, Depends(UserFilterSchema)]
