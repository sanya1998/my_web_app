from app.common.schemas.base import BaseSchema
from app.services.password import PasswordService
from pydantic import EmailStr, computed_field


class UserSchemaBase(BaseSchema):
    email: EmailStr


class UserInputSchema(UserSchemaBase):
    raw_password: str

    @computed_field
    @property
    def hashed_password(self) -> str:
        return PasswordService.get_password_hash(self.raw_password)


class UserCreateSchema(UserSchemaBase):
    hashed_password: str


class UserPasswordUpdateSchema(UserSchemaBase):
    old_password: str
    new_password: str

    @computed_field
    @property
    def old_hashed_password(self) -> str:
        return PasswordService.get_password_hash(self.old_password)

    @computed_field
    @property
    def new_hashed_password(self) -> str:
        return PasswordService.get_password_hash(self.new_password)


class UserUpdateSchema(UserSchemaBase):
    first_name: str | None = None
    last_name: str | None = None


class UserReadSchema(UserUpdateSchema):
    id: int | None = None
