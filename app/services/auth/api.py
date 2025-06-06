import hashlib

from app.common.constants.roles import AllRolesEnum
from app.common.helpers.db import get_columns_by_table
from app.common.schemas.user import UserBaseReadSchema, UserCreateSchema
from app.common.tables import Users
from app.config.common import settings
from app.dependencies.auth.credentials import CredentialsInput
from app.exceptions.services import AlreadyExistsServiceError, NotFoundServiceError, UnauthorizedServiceError
from app.repositories import UserRepo
from app.services.auth.base import BaseAuthService
from pydantic import SecretStr
from starlette.requests import Request


class ApiAuthService(BaseAuthService):
    @BaseAuthService.catcher
    def __init__(self, user_repo: UserRepo, request: Request):
        self.request = request
        super().__init__(user_repo=user_repo)

    @classmethod
    @BaseAuthService.catcher
    def create_and_remember_access_token(cls, email: str, request: Request) -> str:
        access_token = cls.create_access_token(data=dict(sub=email))
        request.session.update({settings.JWT_COOKIE_NAME: access_token})
        return access_token

    @classmethod
    @BaseAuthService.catcher
    def get_password_hash(cls, password: SecretStr) -> str:
        return hashlib.sha256(password.get_secret_value().encode(settings.ENCODING)).hexdigest()

    async def get_user_input(self) -> CredentialsInput:
        form = await self.request.form()
        return CredentialsInput(**form)

    @BaseAuthService.catcher
    async def sign_up(self) -> UserBaseReadSchema:
        user_input = await self.get_user_input()
        if await self.user_repo.is_exists(email=user_input.email):
            raise AlreadyExistsServiceError
        hashed_password_input = self.get_password_hash(user_input.password)
        roles = [AllRolesEnum.USER]  # При регистрации всегда предоставляется роль user
        new_user_create_schema = UserCreateSchema(
            email=user_input.email, hashed_password=hashed_password_input, roles=roles
        )
        new_user = await self.user_repo.create(new_user_create_schema)
        self.create_and_remember_access_token(email=user_input.email, request=self.request)
        return new_user

    @BaseAuthService.catcher
    async def sign_in(self) -> str:
        user_input = await self.get_user_input()
        if await self.user_repo.is_not_exists(email=user_input.email):
            raise NotFoundServiceError
        password_field = get_columns_by_table(Users).hashed_password.name
        hashed_password_db = await self.user_repo.get_object_field(key=password_field, email=user_input.email)
        hashed_password_input = self.get_password_hash(user_input.password)
        if hashed_password_db != hashed_password_input:
            raise UnauthorizedServiceError
        return self.create_and_remember_access_token(email=user_input.email, request=self.request)

    @BaseAuthService.catcher
    def sign_out(self):
        self.request.session.pop(settings.JWT_COOKIE_NAME)

    @BaseAuthService.catcher
    def get_token(self, bearer: str | None = None, header: str | None = None) -> str:
        cookie = self.request.session.get(settings.JWT_COOKIE_NAME)
        return bearer or header or cookie  # TODO: добавить тесты на все способы аутентификации

    @BaseAuthService.catcher
    async def get_user(self, token: str) -> UserBaseReadSchema:
        payload = self.decrypt_access_token(token)
        user = await self.user_repo.get_object(email=payload.get("sub"))
        return user
