from app.common.dependencies.input.users import UserInputDep
from app.common.dependencies.services.authorization import AuthorizationServiceDep
from app.common.exceptions.api.already_exists import AlreadyExistsApiError
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.services.already_exists import AlreadyExistsServiceError
from app.common.exceptions.services.base import BaseServiceError
from app.common.schemas.user import OneUserReadSchema
from fastapi import APIRouter

sign_up_router = APIRouter()


@sign_up_router.post("/sign_up")
async def sign_up(user_input: UserInputDep, auth_service: AuthorizationServiceDep) -> OneUserReadSchema:
    try:
        return await auth_service.sign_up(user_input)
    except AlreadyExistsServiceError:
        raise AlreadyExistsApiError
    except BaseServiceError:
        raise BaseApiError
