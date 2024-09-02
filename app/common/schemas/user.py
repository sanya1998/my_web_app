from typing import List

from app.common.constants.password import PASSWORD_FIELD
from app.common.constants.roles import RolesEnum
from app.common.schemas.base import BaseSchema
from fastapi import Form
from pydantic import EmailStr, Field, SecretStr


class UserSchemaBase(BaseSchema):
    email: EmailStr


class UserInputSchema(UserSchemaBase):
    email: EmailStr = Field(Form())
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
