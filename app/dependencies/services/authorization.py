from typing import Annotated

from app.dependencies.repositories import UserRepoDep, get_user_repo
from app.services import AuthorizationService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


def get_authorization_service(user_repo: UserRepoDep, request: Request):
    return AuthorizationService(user_repo=user_repo, request=request)


AuthorizationServiceDep = Annotated[AuthorizationService, Depends(get_authorization_service)]


def get_authorization_service_by_request_and_session(request: Request, session: AsyncSession) -> AuthorizationService:
    return get_authorization_service(user_repo=get_user_repo(session=session), request=request)
