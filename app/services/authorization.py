import copy
import hashlib
from datetime import datetime, timedelta

import jwt
from app.common.exceptions.services.already_exists import AlreadyExistsServiceError
from app.common.exceptions.services.not_found import NotFoundServiceError
from app.common.exceptions.services.unauthorized import (
    ExpiredSignatureServiceError,
    InvalidAlgorithmServiceError,
    InvalidTokenServiceError,
    MissingRequiredClaimServiceError,
    UnauthorizedServiceError,
)
from app.common.helpers.db import get_columns_by_table
from app.common.schemas.user import UserCreateSchema, UserInputSchema, UserReadSchema
from app.common.tables import Users
from app.config.main import settings
from app.repositories.user import UserRepo
from app.services.base import BaseService
from fastapi import Response
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidAlgorithmError,
    InvalidTokenError,
    MissingRequiredClaimError,
)
from pydantic import SecretStr


class AuthorizationService(BaseService):
    @BaseService.catcher
    def __init__(self, user_repo: UserRepo):
        super().__init__()
        self.user_repo = user_repo

    @BaseService.catcher
    def get_password_hash(self, password: SecretStr) -> str:
        return hashlib.sha256(password.get_secret_value().encode(settings.ENCODING)).hexdigest()

    @BaseService.catcher
    def create_access_token(self, data: dict) -> str:
        to_encode = copy.deepcopy(data)
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(payload=to_encode, key=settings.JWT_SECRET_KEY, algorithm=settings.ENCODE_ALGORITHM)
        return encoded_jwt

    @BaseService.catcher
    def decrypt_access_token(
        self, token: str, key=settings.JWT_SECRET_KEY, algorithms=settings.DECODE_ALGORITHMS
    ) -> dict:
        try:
            payload = jwt.decode(
                jwt=token,
                key=key,
                algorithms=algorithms,
                options={"require": ["exp", "sub"]},
            )
            return payload
        except MissingRequiredClaimError:
            raise MissingRequiredClaimServiceError
        except ExpiredSignatureError:
            raise ExpiredSignatureServiceError
        except InvalidAlgorithmError:
            raise InvalidAlgorithmServiceError
        except InvalidTokenError:
            raise InvalidTokenServiceError

    @BaseService.catcher
    async def get_user_by_access_token(self, token: str) -> UserReadSchema:
        payload = self.decrypt_access_token(token)
        user = await self.user_repo.get_object(email=payload.get("sub"))
        return user

    @BaseService.catcher
    async def sign_up(self, user_input: UserInputSchema):
        if await self.user_repo.is_exists(email=user_input.email):
            raise AlreadyExistsServiceError
        hashed_password_input = self.get_password_hash(user_input.raw_password)
        new_user = UserCreateSchema(email=user_input.email, hashed_password=hashed_password_input)
        return await self.user_repo.create(new_user)

    @BaseService.catcher
    async def sign_in(self, user_input: UserInputSchema):
        if await self.user_repo.is_not_exists(email=user_input.email):
            raise NotFoundServiceError
        password_field = get_columns_by_table(Users).hashed_password.name
        hashed_password_db = await self.user_repo.get_object_field(key=password_field, email=user_input.email)
        hashed_password_input = self.get_password_hash(user_input.raw_password)
        if hashed_password_db != hashed_password_input:
            raise UnauthorizedServiceError

    @BaseService.catcher
    async def sign_out(self, response: Response):
        response.delete_cookie(settings.JWT_COOKIE_NAME)

    @BaseService.catcher
    def create_and_remember_access_token(self, response: Response, email: str):
        access_token = self.create_access_token(data=dict(sub=email))
        response.set_cookie(key=settings.JWT_COOKIE_NAME, value=access_token, httponly=True)
        return access_token
