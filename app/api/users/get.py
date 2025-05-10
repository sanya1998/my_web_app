from typing import Annotated, List

from app.common.dependencies.auth.admin import AdminUserDep
from app.common.dependencies.auth.base import CurrentUserDep
from app.common.dependencies.filters.users import UsersFiltersDep
from app.common.dependencies.repositories.user import UserRepoDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.multiple_results import MultipleResultsApiError
from app.common.exceptions.api.not_found import NotFoundApiError
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.multiple_results import MultipleResultsRepoError
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.schemas.user import UserBaseReadSchema
from fastapi import Path

get_router = VersionedAPIRouter()


@get_router.get("/")
async def get_users_for_admin(
    filters: UsersFiltersDep, user_repo: UserRepoDep, admin: AdminUserDep
) -> List[UserBaseReadSchema]:
    try:
        return await user_repo.get_objects(filters=filters)
    except BaseRepoError:
        raise BaseApiError


@get_router.get("/current")
async def get_current_user(user: CurrentUserDep) -> UserBaseReadSchema:
    return user


@get_router.get("/{object_id}")
async def get_user_for_admin(
    object_id: Annotated[int, Path(gt=0)], user_repo: UserRepoDep, admin: AdminUserDep
) -> UserBaseReadSchema:
    try:
        return await user_repo.get_object(id=object_id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except MultipleResultsRepoError:
        raise MultipleResultsApiError
    except BaseRepoError:
        raise BaseApiError
