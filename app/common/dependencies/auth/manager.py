from typing import Annotated

from app.common.constants.roles import RolesEnum
from app.common.dependencies.auth.base import get_current_user
from app.common.exceptions.api.forbidden import ForbiddenApiError
from app.common.schemas.user import UserBaseReadSchema
from fastapi import Depends


async def get_manager_user(user: Annotated[UserBaseReadSchema, Depends(get_current_user)]):
    if RolesEnum.MANAGER not in user.roles:
        raise ForbiddenApiError
    return user


ManagerUserDep = Annotated[UserBaseReadSchema, Depends(get_manager_user)]
