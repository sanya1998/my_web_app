from typing import Annotated

from app.common.dependencies.filters.base import BaseFiltersSchema
from fastapi import Depends


class UserBaseFiltersSchema(BaseFiltersSchema):
    pass


UsersFiltersDep = Annotated[UserBaseFiltersSchema, Depends(UserBaseFiltersSchema)]
