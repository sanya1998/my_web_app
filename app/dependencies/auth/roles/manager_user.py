from typing import Annotated

from app.common.schemas.user import UserBaseReadSchema
from app.dependencies.auth.token import CurrentUserAnn
from app.dependencies.services import RolesAuthServiceAnn
from app.exceptions.api import ForbiddenApiError
from fastapi import Depends


def get_manager_or_user(auth_service: RolesAuthServiceAnn, user: CurrentUserAnn):
    if not auth_service.authenticate_manager_or_user_by_user(user):
        raise ForbiddenApiError
    return user


ManagerOrUserDep = Depends(get_manager_or_user)
ManagerOrUserAnn = Annotated[UserBaseReadSchema, ManagerOrUserDep]
