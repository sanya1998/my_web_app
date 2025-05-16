from typing import Annotated

from app.common.constants.password import PASSWORD_FIELD
from app.dependencies.input.base import BaseInput
from fastapi import Form
from pydantic import EmailStr, Field, SecretStr, field_serializer
from pydantic_core.core_schema import SerializationInfo

DUMP_SECRET_KEY = "dump_secrets"


class UserInput(BaseInput):
    email: Annotated[EmailStr, Field(description="Email")]  # TODO: rename to username
    password: Annotated[SecretStr, PASSWORD_FIELD]

    @field_serializer("password")
    def dump_secret(self, v: SecretStr, info: SerializationInfo):
        if info.context.get(DUMP_SECRET_KEY):
            return v.get_secret_value()
        return v


# TODO: пока не используется: смена паролей, изменение ролей
class UserPasswordUpdateInputSchema(UserInput):
    new_password: Annotated[SecretStr, PASSWORD_FIELD]


UserInputDep = Annotated[UserInput, Form()]
