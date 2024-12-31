from typing import List

from app.common.dependencies.auth.admin import AdminUserDep
from app.common.dependencies.auth.base import CurrentUserDep
from app.common.dependencies.filters.users import UsersFiltersDep
from app.common.dependencies.repositories.user import UserRepoDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.schemas.user import OneUserReadSchema
from fastapi import APIRouter

get_router = APIRouter()


@get_router.get("/for_admin")
async def get_users_for_admin(
    filters: UsersFiltersDep, user_repo: UserRepoDep, admin: AdminUserDep
) -> List[OneUserReadSchema]:
    try:
        return await user_repo.get_objects(filters=filters)
    except BaseRepoError:
        raise BaseApiError


@get_router.get("/current")
async def get_current_user(user: CurrentUserDep) -> OneUserReadSchema:
    return user
