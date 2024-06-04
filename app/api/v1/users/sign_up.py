from app.common.dependencies.repositories.user import UserRepoDep
from app.common.exceptions.api.already_exists import ApiAlreadyExistsError
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.not_found import RepoNotFoundError
from app.common.schemas.user import UserInputSchema, UserReadSchema
from fastapi import APIRouter

sign_up_router = APIRouter()


@sign_up_router.post("/sign_up")
async def sign_up(user_data: UserInputSchema, user_repo: UserRepoDep) -> UserReadSchema:
    # TODO: надо упростить этот эндпоинт (как вариант: добавить обработку конфликта в sql-запрос)
    try:
        await user_repo.get_object(email=user_data.email)
        raise ApiAlreadyExistsError
    except RepoNotFoundError:
        try:
            return await user_repo.create(user_data)
        except BaseRepoError:
            raise BaseApiError
    except BaseRepoError:
        raise BaseApiError
