from app.config.common import settings
from app.exceptions.services import BaseServiceError
from app.resources.postgres import with_session
from app.services.auth.cms import CmsAuthService
from pydantic import ValidationError
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


class AdminAuth(AuthenticationBackend):
    @with_session
    async def login(self, request: Request, session: AsyncSession) -> bool:
        """
        Выполняется при входе
        """
        try:
            auth_service = CmsAuthService(request=request, session=session)
            access_token = await auth_service.sign_in()
            return await auth_service.authenticate_admin_or_moderator_by_token(access_token)
        except (ValidationError, BaseServiceError):
            return False

    @with_session
    async def logout(self, request: Request, session: AsyncSession) -> bool:
        """
        Выполняется при выходе
        """
        try:
            auth_service = CmsAuthService(request=request, session=session)
            auth_service.sign_out()
            return True
        except BaseServiceError:
            return False

    @with_session
    async def authenticate(self, request: Request, session: AsyncSession) -> bool:
        """
        Выполняется при каждом переходе между страницами
        """
        try:
            auth_service = CmsAuthService(request=request, session=session)
            return await auth_service.authenticate_admin_or_moderator()
        except BaseServiceError:
            return False


authentication_backend = AdminAuth(secret_key=settings.JWT_SECRET_KEY)
