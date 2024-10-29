from typing import List

from app.common.constants.password import PASSWORD_FIELD
from app.common.constants.roles import RolesEnum
from app.common.schemas.base import BaseSchema
from fastapi import Form
from pydantic import EmailStr, Field, SecretStr


class UserBaseSchema(BaseSchema):
    email: EmailStr


class UserInputSchema(UserBaseSchema):
    email: EmailStr = Field(Form())
    raw_password: SecretStr = PASSWORD_FIELD


class UserCreateSchema(UserBaseSchema):
    hashed_password: str


class UserPasswordUpdateSchema(UserBaseSchema):
    old_password: SecretStr = PASSWORD_FIELD
    new_password: SecretStr = PASSWORD_FIELD


class UserDataUpdateSchema(UserBaseSchema):
    first_name: str | None = None
    last_name: str | None = None


class UserRolesUpdateSchema(UserBaseSchema):
    roles: List[RolesEnum] = []


class OneUserReadSchema(UserDataUpdateSchema, UserRolesUpdateSchema):
    id: int


class OneCreatedUserReadSchema(OneUserReadSchema):
    pass


class ManyUsersReadSchema(OneUserReadSchema):
    pass
