from typing import Annotated

from app.common.constants.roles import RolesEnum
from app.common.dependencies.auth.base import get_current_user
from app.common.exceptions.api.forbidden import ForbiddenApiError
from app.common.schemas.user import UserBaseReadSchema
from fastapi import Depends


async def get_admin_user(user: Annotated[UserBaseReadSchema, Depends(get_current_user)]):
    if RolesEnum.ADMIN not in user.roles:
        raise ForbiddenApiError
    return user


AdminUserDep = Annotated[UserBaseReadSchema, Depends(get_admin_user)]
