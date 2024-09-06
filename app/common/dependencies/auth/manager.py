from typing import Annotated

from app.common.constants.roles import RolesEnum
from app.common.dependencies.auth.base import get_current_user
from app.common.exceptions.api.forbidden import ForbiddenApiError
from app.common.schemas.user import UserReadSchema
from fastapi import Depends


async def get_current_manager_user(user: Annotated[UserReadSchema, Depends(get_current_user)]):
    if RolesEnum.MANAGER not in user.roles:
        raise ForbiddenApiError
    return user


CurrentManagerUserDep = Annotated[UserReadSchema, Depends(get_current_manager_user)]