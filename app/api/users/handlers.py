from typing import Annotated, List

from app.common.constants.auth import SIGN_IN_RESULT, SIGN_OUT_RESULT, SignInResult, SignOutResult
from app.common.constants.paths import (
    PATTERN_OBJECT_ID,
    SIGN_IN_PATH,
    SIGN_OUT_PATH,
    SIGN_UP_PATH,
    USERS_CURRENT_PATH,
    USERS_PATH,
)
from app.common.dependencies.auth import AdminUserDep, CurrentUserDep
from app.common.dependencies.filters import UsersFiltersDep
from app.common.dependencies.input import UserInputDep
from app.common.dependencies.repositories import UserRepoDep
from app.common.dependencies.services import AuthorizationServiceDep
from app.common.exceptions.api import (
    AlreadyExistsApiError,
    BaseApiError,
    MultipleResultsApiError,
    NotFoundApiError,
    UnauthorizedApiError,
)
from app.common.exceptions.repositories import BaseRepoError, MultipleResultsRepoError, NotFoundRepoError
from app.common.exceptions.services import (
    AlreadyExistsServiceError,
    BaseServiceError,
    NotFoundServiceError,
    UnauthorizedServiceError,
)
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.helpers.response import BaseResponse
from app.common.schemas.user import UserBaseReadSchema
from fastapi import Path
from starlette import status

router = VersionedAPIRouter(prefix=USERS_PATH, tags=["Users"])


@router.get("/")
async def get_users_for_admin(
    filters: UsersFiltersDep, user_repo: UserRepoDep, admin: AdminUserDep
) -> BaseResponse[List[UserBaseReadSchema]]:
    try:
        users = await user_repo.get_objects(filters=filters)
        return BaseResponse(content=users)
    except BaseRepoError:
        raise BaseApiError


@router.get(USERS_CURRENT_PATH)
async def get_current_user(user: CurrentUserDep) -> BaseResponse[UserBaseReadSchema]:
    return BaseResponse(content=user)


@router.post(SIGN_IN_PATH, response_model=BaseResponse[SignInResult])
async def sign_in(user_input: UserInputDep, auth_service: AuthorizationServiceDep):
    try:
        await auth_service.sign_in(user_input)
        return BaseResponse(content=SIGN_IN_RESULT)
    except NotFoundServiceError:
        raise NotFoundApiError
    except UnauthorizedServiceError:
        raise UnauthorizedApiError
    except BaseServiceError:
        raise BaseApiError


@router.post(SIGN_OUT_PATH, response_model=BaseResponse[SignOutResult])
async def sign_out(auth_service: AuthorizationServiceDep):
    try:
        await auth_service.sign_out()
        return BaseResponse(content=SIGN_OUT_RESULT)
    except BaseServiceError:
        raise BaseApiError


@router.post(SIGN_UP_PATH, response_model=BaseResponse[UserBaseReadSchema], status_code=status.HTTP_201_CREATED)
async def sign_up(user_input: UserInputDep, auth_service: AuthorizationServiceDep):
    try:
        user = await auth_service.sign_up(user_input)
        return BaseResponse(content=user)
    except AlreadyExistsServiceError:
        raise AlreadyExistsApiError
    except BaseServiceError:
        raise BaseApiError


@router.get(PATTERN_OBJECT_ID, response_model=BaseResponse[UserBaseReadSchema])
async def get_user_for_admin(object_id: Annotated[int, Path(gt=0)], user_repo: UserRepoDep, admin: AdminUserDep):
    try:
        user = await user_repo.get_object(id=object_id)
        return BaseResponse(content=user)
    except NotFoundRepoError:
        raise NotFoundApiError
    except MultipleResultsRepoError:
        raise MultipleResultsApiError
    except BaseRepoError:
        raise BaseApiError
