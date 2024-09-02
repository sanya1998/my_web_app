from typing import List

from app.common.constants.roles import RolesEnum
from app.common.schemas.base import BaseSchema
from app.config.main import settings
from fastapi import Form
from pydantic import EmailStr, Field, SecretStr

PASSWORD_FIELD = Field(Form(min_length=settings.PASSWORD_MIN_LENGTH))


class UserSchemaBase(BaseSchema):
    email: EmailStr = Field(Form())


class UserInputSchema(UserSchemaBase):
    raw_password: SecretStr = PASSWORD_FIELD


class UserCreateSchema(UserSchemaBase):
    hashed_password: str


class UserPasswordUpdateSchema(UserSchemaBase):
    old_password: SecretStr = PASSWORD_FIELD
    new_password: SecretStr = PASSWORD_FIELD


class UserDataUpdateSchema(UserSchemaBase):
    first_name: str | None = None
    last_name: str | None = None


class UserRolesUpdateSchema(UserSchemaBase):
    roles: List[RolesEnum] = []


class UserReadSchema(UserDataUpdateSchema, UserRolesUpdateSchema):
    id: int
    email: EmailStr = Field()
