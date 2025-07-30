from typing import Annotated, List

from app.common.constants.paths import PATTERN_OBJECT_ID, USERS_CURRENT_PATH, USERS_PATH
from app.common.constants.tags import TagsEnum
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.helpers.response import BaseResponse
from app.common.schemas.user import UserBaseReadSchema
from app.dependencies.auth.roles.admin import AdminDep
from app.dependencies.auth.token import CurrentUserAnn
from app.dependencies.filters import UsersFiltersDep
from app.dependencies.repositories import UserRepoAnn
from app.exceptions.api import NotFoundApiError
from app.exceptions.repositories import NotFoundRepoError
from fastapi import Path

router = VersionedAPIRouter(prefix=USERS_PATH, tags=[TagsEnum.USERS])


@router.get("/", response_model=BaseResponse[List[UserBaseReadSchema]], dependencies=[AdminDep])
async def get_users_for_admin(filters: UsersFiltersDep, user_repo: UserRepoAnn):
    users = await user_repo.get_objects(filters=filters)
    return BaseResponse(content=users)


@router.get(USERS_CURRENT_PATH, response_model=BaseResponse[UserBaseReadSchema])
async def get_current_user(user: CurrentUserAnn):
    return BaseResponse(content=user)


@router.get(PATTERN_OBJECT_ID, response_model=BaseResponse[UserBaseReadSchema], dependencies=[AdminDep])
async def get_user_for_admin(object_id: Annotated[int, Path(gt=0)], user_repo: UserRepoAnn):
    try:
        user = await user_repo.get_object(id=object_id)
        return BaseResponse(content=user)
    except NotFoundRepoError:
        raise NotFoundApiError(detail="User was not found")
