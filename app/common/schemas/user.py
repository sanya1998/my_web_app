from typing import List

from app.common.constants.roles import RolesEnum
from app.common.schemas.base import BaseSchema
from fastapi import Body
from pydantic import EmailStr, Field, SecretStr


class UserSchemaBase(BaseSchema):
    email: EmailStr = Field(Body())


class UserInputSchema(UserSchemaBase):
    raw_password: SecretStr = Field(Body())


class UserCreateSchema(UserSchemaBase):
    hashed_password: str


class UserPasswordUpdateSchema(UserSchemaBase):
    old_password: SecretStr
    new_password: SecretStr


class UserDataUpdateSchema(UserSchemaBase):
    first_name: str | None = None
    last_name: str | None = None


class UserRolesUpdateSchema(UserSchemaBase):
    roles: List[RolesEnum] = []


class UserReadSchema(UserDataUpdateSchema, UserRolesUpdateSchema):
    id: int
