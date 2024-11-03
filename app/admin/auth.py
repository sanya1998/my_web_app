from app.common.dependencies.auth.admin import get_current_admin_user
from app.common.dependencies.auth.base import get_current_user_by_request_and_session
from app.common.dependencies.auth.moderator import get_current_moderator_user
from app.common.dependencies.services.authorization import (
    get_authorization_service_by_request_and_session,
)
from app.common.exceptions.api.unauthorized import MissingTokenApiError
from app.common.exceptions.services.base import BaseServiceError
from app.common.schemas.user import UserInputSchema
from app.config.main import settings
from app.resources.postgres import async_session
from pydantic import SecretStr
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request


# TODO: в случае не успеха делать редирект на форму входа (в случае expired, например), в идеале logout
# TODO: при выходе из приложения ошибка: The garbage collector is trying to clean up non-checked-in connection ...
class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        """
        Выполняется при входе
        """
        form = await request.form()
        email, password = form["username"], SecretStr(form["password"])
        try:
            async with async_session() as session:  # TODO: громоздко.
                auth_service = await get_authorization_service_by_request_and_session(request, session)
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
            async with async_session() as session:  # TODO: громоздко.
                user = await get_current_user_by_request_and_session(request, session)
                if await get_current_admin_user(user) or await get_current_moderator_user(user):
                    return True
                return False
        except (BaseServiceError, MissingTokenApiError):
            return False


authentication_backend = AdminAuth(secret_key=settings.JWT_SECRET_KEY)
