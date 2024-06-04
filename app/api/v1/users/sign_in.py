from app.common.dependencies.repositories.user import UserRepoDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.not_found import ApiNotFoundError
from app.common.exceptions.api.unauthorized import ApiUnauthorizedError
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.not_found import RepoNotFoundError
from app.common.schemas.user import UserInputSchema
from app.config.main import settings
from app.services.authorization import AuthorizationService
from fastapi import APIRouter, Response

sign_in_router = APIRouter()


@sign_in_router.post("/sign_in")
async def sign_in(response: Response, user_input: UserInputSchema, user_repo: UserRepoDep):
    try:
        hashed_password = await user_repo.get_object_field(key="hashed_password", email=user_input.email)
        if not AuthorizationService.verify(user_input.hashed_password, hashed_password):
            raise ApiUnauthorizedError
        user_from_db = await user_repo.get_object(email=user_input.email)
        access_token = AuthorizationService.create_access_token(data=dict(sub=user_from_db.id))
        # TODO: При регистрации тоже занести в куки
        response.set_cookie(key=settings.ACCESS_TOKEN_VARIABLE, value=access_token, httponly=True)
        return dict(access_token=access_token)

    except RepoNotFoundError:
        raise ApiNotFoundError
    except BaseRepoError:
        raise BaseApiError
