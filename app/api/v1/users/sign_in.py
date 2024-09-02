from app.common.dependencies.filters.users import UserInputDep
from app.common.dependencies.services.authorization import AuthorizationServiceDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.not_found import NotFoundApiError
from app.common.exceptions.api.unauthorized import UnauthorizedApiError
from app.common.exceptions.services.base import BaseServiceError
from app.common.exceptions.services.not_found import NotFoundServiceError
from app.common.exceptions.services.unauthorized import UnauthorizedServiceError
from fastapi import APIRouter, Response

sign_in_router = APIRouter()


@sign_in_router.post("/sign_in")
async def sign_in(user_input: UserInputDep, auth_service: AuthorizationServiceDep, response: Response) -> dict:
    try:
        await auth_service.sign_in(user_input)
        access_token = auth_service.create_and_remember_access_token(response=response, email=user_input.email)
        return dict(access_token=access_token)
    except NotFoundServiceError:
        raise NotFoundApiError
    except UnauthorizedServiceError:
        raise UnauthorizedApiError
    except BaseServiceError:
        raise BaseApiError
