from typing import Annotated

from app.common.schemas.user import UserBaseReadSchema
from app.dependencies.auth.token import CurrentUserAnn
from app.dependencies.services import RolesAuthServiceAnn
from app.exceptions.api import ForbiddenApiError
from fastapi import Depends


async def get_manager(auth_service: RolesAuthServiceAnn, user: CurrentUserAnn):
    if not auth_service.authenticate_manager_by_user(user):
        raise ForbiddenApiError
    return user


ManagerDep = Depends(get_manager)
ManagerAnn = Annotated[UserBaseReadSchema, ManagerDep]
