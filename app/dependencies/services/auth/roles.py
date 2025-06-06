from typing import Annotated

from app.dependencies.repositories import UserRepoAnn
from app.services.auth import RolesAuthService
from fastapi import Depends


def get_roles_auth_service(user_repo: UserRepoAnn) -> RolesAuthService:
    return RolesAuthService(user_repo=user_repo)


RolesAuthServiceAnn = Annotated[RolesAuthService, Depends(get_roles_auth_service)]
