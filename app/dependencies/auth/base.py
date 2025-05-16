from typing import Annotated

from app.common.schemas.user import UserBaseReadSchema
from app.config.common import settings
from app.dependencies.services import AuthorizationServiceDep
from app.exceptions.api import (
    ExpiredSignatureApiError,
    InvalidTokenApiError,
    MissingRequiredClaimApiError,
    MissingTokenApiError,
    NotFoundApiError,
)
from app.exceptions.services import (
    ExpiredSignatureServiceError,
    InvalidTokenServiceError,
    MissingRequiredClaimServiceError,
    NotFoundServiceError,
)
from fastapi import Depends, Request


def get_token(request: Request) -> str:
    if token := request.session.get(settings.JWT_COOKIE_NAME):
        return token
    else:
        raise MissingTokenApiError


async def get_current_user(
    auth_service: AuthorizationServiceDep, token: Annotated[str, Depends(get_token)]
) -> UserBaseReadSchema:
    try:
        return await auth_service.get_user_by_access_token(token)
    except MissingRequiredClaimServiceError:
        raise MissingRequiredClaimApiError
    except ExpiredSignatureServiceError:
        raise ExpiredSignatureApiError
    except InvalidTokenServiceError:
        raise InvalidTokenApiError
    except NotFoundServiceError:
        raise NotFoundApiError


CurrentUserDep = Annotated[UserBaseReadSchema, Depends(get_current_user)]
