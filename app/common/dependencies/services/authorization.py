from typing import Annotated

from app.common.dependencies.repositories.user import UserRepoDep
from app.services.authorization import AuthorizationService
from fastapi import Depends


def get_authorization_service(user_repo: UserRepoDep):
    return AuthorizationService(user_repo=user_repo)


AuthorizationServiceDep = Annotated[AuthorizationService, Depends(get_authorization_service)]
