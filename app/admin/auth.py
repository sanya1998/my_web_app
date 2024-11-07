from app.common.dependencies.auth.admin_moderator import (
    get_admin_or_moderator_by_request,
)
from app.common.dependencies.services.authorization import (
    get_authorization_service_by_request_and_session,
)
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.forbidden import ForbiddenApiError
from app.common.exceptions.api.unauthorized import MissingTokenApiError, ExpiredSignatureApiError
from app.common.exceptions.services.base import BaseServiceError
from app.common.exceptions.services.unauthorized import ExpiredSignatureServiceError
from app.common.schemas.user import UserInputSchema
from app.config.main import settings
from app.resources.postgres import with_session
from pydantic import SecretStr
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


class AdminAuth(AuthenticationBackend):
    @with_session
    async def login(self, request: Request, session: AsyncSession) -> bool:
        """
        Выполняется при входе
        """
        form = await request.form()
        email, password = form["username"], SecretStr(form["password"])
        try:
            auth_service = get_authorization_service_by_request_and_session(request, session)
            await auth_service.sign_in(UserInputSchema(email=email, raw_password=password))
            return True
        except BaseServiceError:
            return False

    async def logout(self, request: Request) -> bool:
        """
        Выполняется при выходе
        """
        request.session.pop(settings.JWT_COOKIE_NAME, None)
        return True

    async def authenticate(self, request: Request) -> bool:
        """
        Выполняется при каждом переходе между страницами
        """
        try:
            await get_admin_or_moderator_by_request(request)
            return True
        except (BaseServiceError, BaseApiError):
            return False


authentication_backend = AdminAuth(secret_key=settings.JWT_SECRET_KEY)
