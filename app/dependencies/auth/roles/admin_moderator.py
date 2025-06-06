from typing import Annotated

from app.common.schemas.user import UserBaseReadSchema
from app.dependencies.auth.token import CurrentUserAnn
from app.dependencies.services import RolesAuthServiceAnn
from app.exceptions.api import ForbiddenApiError
from fastapi import Depends


def get_admin_or_moderator(auth_service: RolesAuthServiceAnn, user: CurrentUserAnn):
    if not auth_service.authenticate_admin_or_moderator_by_user(user):
        raise ForbiddenApiError
    return user


AdminOrModeratorDep = Depends(get_admin_or_moderator)
AdminOrModeratorAnn = Annotated[UserBaseReadSchema, AdminOrModeratorDep]
