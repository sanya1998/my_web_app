from typing import Annotated

from app.common.dependencies.repositories.user import get_user_repo
from app.common.dependencies.services.authorization import (
    AuthorizationServiceDep,
    get_authorization_service,
)
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.not_found import NotFoundApiError
from app.common.exceptions.api.unauthorized import (
    ExpiredSignatureApiError,
    InvalidTokenApiError,
    MissingRequiredClaimApiError,
    MissingTokenApiError,
)
from app.common.exceptions.services.base import BaseServiceError
from app.common.exceptions.services.not_found import NotFoundServiceError
from app.common.exceptions.services.unauthorized import (
    ExpiredSignatureServiceError,
    InvalidTokenServiceError,
    MissingRequiredClaimServiceError,
)
from app.common.schemas.user import OneUserReadSchema
from app.config.main import settings
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession


def get_token(request: Request) -> str:
    if token := request.session.get(settings.JWT_COOKIE_NAME):
        return token
    else:
        raise MissingTokenApiError


async def get_current_user(
    auth_service: AuthorizationServiceDep, token: Annotated[str, Depends(get_token)]
) -> OneUserReadSchema:
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
    except BaseServiceError:
        raise BaseApiError


CurrentUserDep = Annotated[OneUserReadSchema, Depends(get_current_user)]


async def get_current_user_by_request_and_session(request: Request, session: AsyncSession) -> OneUserReadSchema:
    user = await get_current_user(
        auth_service=get_authorization_service(user_repo=get_user_repo(session=session), request=request),
        token=get_token(request),
    )
    return user
