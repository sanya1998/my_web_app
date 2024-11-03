from typing import Annotated

from app.common.dependencies.repositories.user import UserRepoDep, get_user_repo
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.services.base import BaseServiceError
from app.services.authorization import AuthorizationService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


def get_authorization_service(user_repo: UserRepoDep, request: Request):
    try:
        return AuthorizationService(user_repo=user_repo, request=request)
    except BaseServiceError:
        raise BaseApiError


AuthorizationServiceDep = Annotated[AuthorizationService, Depends(get_authorization_service)]


async def get_authorization_service_by_request_and_session(
    request: Request, session: AsyncSession
) -> AuthorizationService:
    auth_service = get_authorization_service(user_repo=get_user_repo(session=session), request=request)
    return auth_service
