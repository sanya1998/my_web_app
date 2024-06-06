from typing import Annotated

from app.common.dependencies.services.authorization import AuthorizationServiceDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.unauthorized import UnauthorizedApiError
from app.common.exceptions.services.base import BaseServiceError
from app.common.schemas.user import UserInputSchema, UserReadSchema
from app.config.main import settings
from fastapi import Depends, Request


def get_token(request: Request):
    token = request.cookies.get(settings.ACCESS_TOKEN_VARIABLE)
    if not token:
        raise UnauthorizedApiError(detail="Токен отсутствует.")
    return token


async def get_current_user(auth_service: AuthorizationServiceDep, token: Annotated[str, Depends(get_token)]):
    try:
        return await auth_service.decrypt_access_token(token)
    except BaseServiceError:
        raise BaseApiError


CurrentUserDep = Annotated[UserReadSchema, Depends(get_current_user)]
UserInputDep = Annotated[UserInputSchema, Depends(UserInputSchema)]
