from typing import List

from app.common.constants.roles import RolesEnum
from app.common.schemas.base import BaseSchema
from pydantic import EmailStr


class UserBaseSchema(BaseSchema):
    email: EmailStr


class UserCreateSchema(UserBaseSchema):
    hashed_password: str


class UserDataUpdateSchema(UserBaseSchema):
    first_name: str | None = None
    last_name: str | None = None


class UserBaseReadSchema(UserDataUpdateSchema):
    id: int
    roles: List[RolesEnum] = list()
