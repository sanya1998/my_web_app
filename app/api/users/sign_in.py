from app.common.dependencies.input.users import UserInputDep
from app.common.dependencies.services.authorization import AuthorizationServiceDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.not_found import NotFoundApiError
from app.common.exceptions.api.unauthorized import UnauthorizedApiError
from app.common.exceptions.services.base import BaseServiceError
from app.common.exceptions.services.not_found import NotFoundServiceError
from app.common.exceptions.services.unauthorized import UnauthorizedServiceError
from app.common.helpers.api_version import VersionedAPIRouter

sign_in_router = VersionedAPIRouter()


@sign_in_router.post("/sign_in")
async def sign_in(user_input: UserInputDep, auth_service: AuthorizationServiceDep) -> None:
    try:
        await auth_service.sign_in(user_input)
    except NotFoundServiceError:
        raise NotFoundApiError
    except UnauthorizedServiceError:
        raise UnauthorizedApiError
    except BaseServiceError:
        raise BaseApiError
