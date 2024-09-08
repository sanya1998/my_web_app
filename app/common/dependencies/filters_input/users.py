from typing import Annotated

from app.common.dependencies.filters_input.base import BaseFiltersInput
from fastapi import Depends


class UserFiltersInput(BaseFiltersInput):
    pass


UsersFiltersDep = Annotated[UserFiltersInput, Depends(UserFiltersInput)]
