from typing import Annotated

from app.common.constants.paths import SIGN_IN_URL
from app.common.schemas.user import UserBaseReadSchema
from app.config.common import settings
from app.dependencies.services import ApiAuthServiceAnn
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
from fastapi import Depends
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer

AuthHeaderAnn = Annotated[str, Depends(APIKeyHeader(name=settings.JWT_COOKIE_NAME, auto_error=False))]
OAuth2PasswordBearerAnn = Annotated[str, Depends(OAuth2PasswordBearer(tokenUrl=SIGN_IN_URL, auto_error=False))]


def get_token(auth_service: ApiAuthServiceAnn, header: AuthHeaderAnn, bearer: OAuth2PasswordBearerAnn) -> str:
    if token := auth_service.get_token(bearer=bearer, header=header):
        return token
    else:
        raise MissingTokenApiError


async def get_user(auth_service: ApiAuthServiceAnn, token: Annotated[str, Depends(get_token)]) -> UserBaseReadSchema:
    try:
        return await auth_service.get_user(token)
    except MissingRequiredClaimServiceError:
        raise MissingRequiredClaimApiError
    except ExpiredSignatureServiceError:
        raise ExpiredSignatureApiError
    except InvalidTokenServiceError:
        raise InvalidTokenApiError
    except NotFoundServiceError:
        raise NotFoundApiError


CurrentUserDep = Depends(get_user)
CurrentUserAnn = Annotated[UserBaseReadSchema, CurrentUserDep]
