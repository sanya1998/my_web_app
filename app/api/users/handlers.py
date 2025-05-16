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
from app.common.constants.tags import TagsEnum
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.helpers.response import BaseResponse
from app.common.schemas.user import UserBaseReadSchema
from app.dependencies.auth import AdminUserDep, CurrentUserDep
from app.dependencies.filters import UsersFiltersDep
from app.dependencies.input import UserInputDep
from app.dependencies.repositories import UserRepoDep
from app.dependencies.services import AuthorizationServiceDep
from app.exceptions.api import (
    AlreadyExistsApiError,
    NotFoundApiError,
    UnauthorizedApiError,
)
from app.exceptions.repositories import NotFoundRepoError
from app.exceptions.services import (
    AlreadyExistsServiceError,
    NotFoundServiceError,
    UnauthorizedServiceError,
)
from fastapi import Path
from starlette import status

router = VersionedAPIRouter(prefix=USERS_PATH, tags=[TagsEnum.USERS])


@router.get("/", response_model=BaseResponse[List[UserBaseReadSchema]])
async def get_users_for_admin(filters: UsersFiltersDep, user_repo: UserRepoDep, admin: AdminUserDep):
    users = await user_repo.get_objects(filters=filters)
    return BaseResponse(content=users)


@router.get(USERS_CURRENT_PATH, response_model=BaseResponse[UserBaseReadSchema])
async def get_current_user(user: CurrentUserDep):
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


@router.post(SIGN_OUT_PATH, response_model=BaseResponse[SignOutResult])
async def sign_out(auth_service: AuthorizationServiceDep):
    await auth_service.sign_out()
    return BaseResponse(content=SIGN_OUT_RESULT)


@router.post(SIGN_UP_PATH, response_model=BaseResponse[UserBaseReadSchema], status_code=status.HTTP_201_CREATED)
async def sign_up(user_input: UserInputDep, auth_service: AuthorizationServiceDep):
    try:
        user = await auth_service.sign_up(user_input)
        return BaseResponse(content=user)
    except AlreadyExistsServiceError:
        raise AlreadyExistsApiError


@router.get(PATTERN_OBJECT_ID, response_model=BaseResponse[UserBaseReadSchema])
async def get_user_for_admin(object_id: Annotated[int, Path(gt=0)], user_repo: UserRepoDep, admin: AdminUserDep):
    try:
        user = await user_repo.get_object(id=object_id)
        return BaseResponse(content=user)
    except NotFoundRepoError:
        raise NotFoundApiError(detail="User was not found")
