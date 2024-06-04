from app.common.schemas.base import BaseSchema
from pydantic import EmailStr, SecretStr


class UserSchemaBase(BaseSchema):
    email: EmailStr


class UserInputSchema(UserSchemaBase):
    raw_password: SecretStr


class UserCreateSchema(UserSchemaBase):
    hashed_password: str


class UserPasswordUpdateSchema(UserSchemaBase):
    old_password: SecretStr
    new_password: SecretStr


class UserUpdateSchema(UserSchemaBase):
    first_name: str | None = None
    last_name: str | None = None


class UserReadSchema(UserUpdateSchema):
    id: int | None = None
