from app.common.schemas.base import BaseSchema


class SignInResult(BaseSchema):
    success: bool


class SignOutResult(BaseSchema):
    success: bool


SIGN_IN_RESULT = SignInResult(success=True)
SIGN_OUT_RESULT = SignOutResult(success=True)
