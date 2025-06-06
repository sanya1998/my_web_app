from typing import Annotated

from app.config.common import settings
from fastapi import Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr, SecretStr


class CredentialsInput(OAuth2PasswordRequestForm):
    def __init__(
        self,
        *,
        username: Annotated[EmailStr, Form(description="Электронная почта")],
        password: Annotated[SecretStr, Form(min_length=settings.PASSWORD_MIN_LENGTH)],
    ):
        password_str = password if isinstance(password, str) else password.get_secret_value()
        password_secret = password if isinstance(password, SecretStr) else SecretStr(password)
        super().__init__(username=username, password=password_str)
        self.email = username
        self.password = password_secret

    def model_dump(self):
        return dict(username=self.email, password=self.password.get_secret_value())


CredentialsInputDep = Depends(CredentialsInput)
