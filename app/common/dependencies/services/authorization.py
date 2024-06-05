from typing import Annotated

from app.common.dependencies.repositories.user import UserRepoDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.services.base import BaseServiceError
from app.services.authorization import AuthorizationService
from fastapi import Depends


def get_authorization_service(user_repo: UserRepoDep):
    try:
        return AuthorizationService(user_repo=user_repo)
    except BaseServiceError:
        raise BaseApiError


AuthorizationServiceDep = Annotated[AuthorizationService, Depends(get_authorization_service)]
