from typing import Annotated

from app.dependencies.repositories import UserRepoAnn
from app.services.auth import ApiAuthService
from fastapi import Depends
from starlette.requests import Request


def get_api_auth_service(user_repo: UserRepoAnn, request: Request) -> ApiAuthService:
    return ApiAuthService(user_repo=user_repo, request=request)


ApiAuthServiceAnn = Annotated[ApiAuthService, Depends(get_api_auth_service)]
