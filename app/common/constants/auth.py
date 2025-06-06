from app.common.schemas.base import BaseSchema


class SignOutResult(BaseSchema):
    success: bool


SIGN_OUT_RESULT = SignOutResult(success=True)
