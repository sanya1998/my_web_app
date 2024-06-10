from typing import Annotated

from app.common.constants.roles import RolesEnum
from app.common.dependencies.services.authorization import AuthorizationServiceDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.forbidden import ForbiddenApiError
from app.common.exceptions.api.unauthorized import UnauthorizedApiError
from app.common.exceptions.services.base import BaseServiceError
from app.common.schemas.user import UserReadSchema
from app.config.main import settings
from fastapi import Depends, Request


def get_token(request: Request):
    token = request.cookies.get(settings.JWT_COOKIE_NAME)
    if not token:
        raise UnauthorizedApiError(detail="Токен отсутствует.")
    return token


async def get_current_user(auth_service: AuthorizationServiceDep, token: Annotated[str, Depends(get_token)]):
    try:
        return await auth_service.decrypt_access_token(token)
    except BaseServiceError:
        raise BaseApiError


async def get_current_admin_user(auth_service: AuthorizationServiceDep, token: Annotated[str, Depends(get_token)]):
    try:
        user = await auth_service.decrypt_access_token(token)
        if RolesEnum.ADMIN not in user.roles:
            raise ForbiddenApiError
        return user
    except BaseServiceError:
        raise BaseApiError


CurrentUserDep = Annotated[UserReadSchema, Depends(get_current_user)]
CurrentAdminUserDep = Annotated[UserReadSchema, Depends(get_current_admin_user)]
