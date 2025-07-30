from pydantic import BaseModel


class PingResult(BaseModel):
    api_version: str
    success: bool


class WelcomeMessage(BaseModel):
    message: str


PING_RESULT_V1 = PingResult(api_version="v1", success=True)
PING_RESULT_V2 = PingResult(api_version="v2", success=True)

WELCOME_MESSAGE = WelcomeMessage(message="Welcome to the API")
