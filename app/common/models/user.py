from typing import List

from app.common.constants.roles import AllRolesEnum
from app.common.models.base import BaseSchema, BaseSQLModel, IdMixin
from pydantic import EmailStr
from sqlalchemy import BigInteger, Column, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field


class UserBaseSchema(BaseSchema):
    email: EmailStr


class Users(BaseSQLModel, UserBaseSchema, table=True):
    id: int = Field(sa_column=Column(BigInteger, primary_key=True, autoincrement=False))
    email: EmailStr = Field(sa_column=Column(String, unique=True))  # TODO: String ?
    first_name: str | None = None
    last_name: str | None = None
    # TODO: RolesEnum (jit": "off" to improve ENUM)
    roles: List[AllRolesEnum] = Field(sa_column=Column(ARRAY(String), default=list()))
    hashed_password: str

    def __str__(self):
        return f"{self.email}"


class UserRolesSchema(UserBaseSchema):
    roles: List[AllRolesEnum]


class UserHashedPasswordSchema(UserBaseSchema):
    hashed_password: str


class UserCreateSchema(UserHashedPasswordSchema, UserRolesSchema):
    hashed_password: str


class UserDataUpdateSchema(UserBaseSchema):
    first_name: str | None = None
    last_name: str | None = None


class UserBaseReadSchema(UserDataUpdateSchema, UserRolesSchema):
    id: int
