from typing import Annotated

from app.common.constants.password import PASSWORD_FIELD
from app.common.dependencies.input.base import BaseInput
from fastapi import Form
from pydantic import EmailStr, SecretStr


class UserInput(BaseInput):
    email: EmailStr
    password: Annotated[SecretStr, PASSWORD_FIELD]


# TODO: пока не используется: смена паролей, изменение ролей
class UserPasswordUpdateInputSchema(UserInput):
    new_password: Annotated[SecretStr, PASSWORD_FIELD]


UserInputDep = Annotated[UserInput, Form()]
