from typing import Annotated

from app.common.constants.roles import AllRolesEnum
from app.common.schemas.user import UserBaseReadSchema
from app.dependencies.auth.base import get_current_user, get_token
from app.dependencies.services.authorization import get_authorization_service_by_request_and_session
from app.exceptions.api import ForbiddenApiError
from app.resources.postgres import with_session
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


def get_admin_or_moderator_user(user: Annotated[UserBaseReadSchema, Depends(get_current_user)]):
    if {AllRolesEnum.ADMIN, AllRolesEnum.MODERATOR}.isdisjoint(user.roles):
        raise ForbiddenApiError
    return user


AdminOrModeratorUserDep = Depends(get_admin_or_moderator_user)
AdminOrModeratorUserAnn = Annotated[UserBaseReadSchema, AdminOrModeratorUserDep]


@with_session
async def get_admin_or_moderator_by_request(request: Request, session: AsyncSession) -> UserBaseReadSchema:
    user = get_admin_or_moderator_user(
        user=await get_current_user(
            auth_service=get_authorization_service_by_request_and_session(request=request, session=session),
            token=get_token(request),
        )
    )
    return user
