from typing import Annotated

from app.common.constants.roles import RolesEnum
from app.common.dependencies.auth.base import get_current_user
from app.common.exceptions.api.forbidden import ForbiddenApiError
from app.common.schemas.user import OneUserReadSchema
from fastapi import Depends


async def get_current_admin_user(user: Annotated[OneUserReadSchema, Depends(get_current_user)]):
    if RolesEnum.ADMIN not in user.roles:
        raise ForbiddenApiError
    return user


CurrentAdminUserDep = Annotated[OneUserReadSchema, Depends(get_current_admin_user)]
