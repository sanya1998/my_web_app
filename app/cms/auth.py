from app.exceptions.services import BaseServiceError
from app.services.auth.cms import CmsAuthService
from pydantic import ValidationError
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


class AdminAuth(AuthenticationBackend):
    def __init__(self, session_factory, secret_key: str):
        self.session_factory = session_factory
        super().__init__(secret_key=secret_key)

    @staticmethod
    def _with_session(method):
        """Внутренний декоратор для работы с сессией"""

        async def wrapper(self, request: Request, *args, **kwargs):
            async with self.session_factory() as session:
                try:
                    return await method(self, request, session, *args, **kwargs)
                except Exception:
                    await session.rollback()
                    raise

        return wrapper

    @_with_session
    async def login(self, request: Request, session: AsyncSession) -> bool:
        try:
            auth_service = CmsAuthService(request=request, session=session)
            access_token = await auth_service.sign_in()
            return await auth_service.authenticate_admin_or_moderator_by_token(access_token)
        except (ValidationError, BaseServiceError):
            return False

    @_with_session
    async def logout(self, request: Request, session: AsyncSession) -> bool:
        try:
            auth_service = CmsAuthService(request=request, session=session)
            auth_service.sign_out()
            return True
        except BaseServiceError:
            return False

    @_with_session
    async def authenticate(self, request: Request, session: AsyncSession) -> bool:
        try:
            auth_service = CmsAuthService(request=request, session=session)
            return await auth_service.authenticate_admin_or_moderator()
        except BaseServiceError:
            return False
