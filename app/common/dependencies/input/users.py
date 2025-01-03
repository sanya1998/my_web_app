from typing import Annotated

from app.common.constants.password import PASSWORD_FIELD
from app.common.dependencies.input.base import BaseInput
from fastapi import Depends, Form
from pydantic import EmailStr, Field, SecretStr


class UserInput(BaseInput):
    email: EmailStr = Field(Form())
    password: SecretStr = PASSWORD_FIELD


# TODO: пока не используется: смена паролей, изменение ролей
class UserPasswordUpdateInputSchema(UserInput):
    new_password: SecretStr = PASSWORD_FIELD


UserInputDep = Annotated[UserInput, Depends(UserInput)]
