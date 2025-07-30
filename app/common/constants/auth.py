from pydantic import BaseModel


class SignOutResult(BaseModel):
    success: bool


SIGN_OUT_RESULT = SignOutResult(success=True)
