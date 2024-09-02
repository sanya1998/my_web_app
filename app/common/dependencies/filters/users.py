from typing import Annotated

from app.common.dependencies.filters.base import BaseFilterSchema
from app.common.schemas.user import UserInputSchema
from fastapi import Depends


class UserFilterSchema(BaseFilterSchema):
    pass


UserInputDep = Annotated[UserInputSchema, Depends(UserInputSchema)]
UserFiltersDep = Annotated[UserFilterSchema, Depends(UserFilterSchema)]
