from typing import Annotated

from app.common.constants.roles import AllRolesEnum
from app.common.schemas.user import UserBaseReadSchema
from app.dependencies.auth.base import get_current_user
from app.exceptions.api import ForbiddenApiError
from fastapi import Depends


def get_manager_or_user(user: Annotated[UserBaseReadSchema, Depends(get_current_user)]):
    if {AllRolesEnum.MANAGER, AllRolesEnum.USER}.isdisjoint(user.roles):
        raise ForbiddenApiError
    return user


ManagerOrUserDep = Depends(get_manager_or_user)
ManagerOrUserAnn = Annotated[UserBaseReadSchema, ManagerOrUserDep]
