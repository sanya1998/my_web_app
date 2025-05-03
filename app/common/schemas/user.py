from typing import List

from app.common.constants.roles import AllRolesEnum
from app.common.schemas.base import BaseSchema
from pydantic import EmailStr


class UserBaseSchema(BaseSchema):
    email: EmailStr


class UserRolesSchema(UserBaseSchema):
    roles: List[AllRolesEnum] = list()


class UserHashedPasswordSchema(UserBaseSchema):
    hashed_password: str


class UserCreateSchema(UserHashedPasswordSchema, UserRolesSchema):
    hashed_password: str


class UserDataUpdateSchema(UserBaseSchema):
    first_name: str | None = None
    last_name: str | None = None


class UserBaseReadSchema(UserDataUpdateSchema, UserRolesSchema):
    id: int
