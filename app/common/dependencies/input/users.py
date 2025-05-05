from typing import Annotated

from app.common.constants.password import PASSWORD_BODY
from app.common.dependencies.input.base import BaseInput
from fastapi import Form
from pydantic import EmailStr, SecretStr


class UserInput(BaseInput):
    email: EmailStr
    password: Annotated[SecretStr, PASSWORD_BODY]


# TODO: пока не используется: смена паролей, изменение ролей
class UserPasswordUpdateInputSchema(UserInput):
    new_password: Annotated[SecretStr, PASSWORD_BODY]


UserInputDep = Annotated[UserInput, Form()]
