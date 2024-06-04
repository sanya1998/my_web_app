from app.common.dependencies.services.authorization import AuthorizationServiceDep
from app.common.exceptions.api.already_exists import AlreadyExistsApiError
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.services.already_exists import AlreadyExistsServiceError
from app.common.exceptions.services.base import BaseServiceError
from app.common.schemas.user import UserInputSchema, UserReadSchema
from fastapi import APIRouter, Response

sign_up_router = APIRouter()


@sign_up_router.post("/sign_up")
async def sign_up(
    user_input: UserInputSchema, auth_service: AuthorizationServiceDep, response: Response
) -> UserReadSchema:
    try:
        new_user = await auth_service.sign_up(user_input)
        await auth_service.create_and_remember_access_token(response=response, email=user_input.email)
        return new_user
    except AlreadyExistsServiceError:
        raise AlreadyExistsApiError
    except BaseServiceError:
        raise BaseApiError
