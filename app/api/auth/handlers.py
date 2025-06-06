from app.common.constants.auth import SIGN_OUT_RESULT, SignOutResult
from app.common.constants.paths import AUTH_PATH, SIGN_IN_PATH, SIGN_OUT_PATH, SIGN_UP_PATH
from app.common.constants.tags import TagsEnum
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.helpers.response import BaseResponse, TokenResponse
from app.common.schemas.user import UserBaseReadSchema
from app.dependencies.auth.credentials import CredentialsInputDep
from app.dependencies.services import ApiAuthServiceAnn
from app.exceptions.api import AlreadyExistsApiError, NotFoundApiError, UnauthorizedApiError
from app.exceptions.services import AlreadyExistsServiceError, NotFoundServiceError, UnauthorizedServiceError
from starlette import status

router = VersionedAPIRouter(prefix=AUTH_PATH, tags=[TagsEnum.AUTH])


@router.post(SIGN_IN_PATH, response_model=TokenResponse, dependencies=[CredentialsInputDep])
async def sign_in(auth_service: ApiAuthServiceAnn):
    try:
        access_token = await auth_service.sign_in()
        return TokenResponse(access_token=access_token)
    except NotFoundServiceError:
        raise NotFoundApiError
    except UnauthorizedServiceError:
        raise UnauthorizedApiError


@router.post(SIGN_OUT_PATH, response_model=BaseResponse[SignOutResult])
async def sign_out(auth_service: ApiAuthServiceAnn):
    auth_service.sign_out()
    return BaseResponse(content=SIGN_OUT_RESULT)


@router.post(
    SIGN_UP_PATH,
    response_model=BaseResponse[UserBaseReadSchema],
    status_code=status.HTTP_201_CREATED,
    dependencies=[CredentialsInputDep],
)
async def sign_up(auth_service: ApiAuthServiceAnn):
    try:
        user = await auth_service.sign_up()
        return BaseResponse(content=user)
    except AlreadyExistsServiceError:
        raise AlreadyExistsApiError
