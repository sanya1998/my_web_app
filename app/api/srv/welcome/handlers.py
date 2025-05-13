from app.common.constants.srv import WELCOME_MESSAGE, WelcomeMessage
from app.common.helpers.response import BaseResponse
from fastapi import APIRouter

router = APIRouter()


@router.get(path="/", response_model=BaseResponse[WelcomeMessage])
def welcome():
    """
    Приветственное сообщение
    """
    # TODO: HTMLResponse
    return BaseResponse(content=WELCOME_MESSAGE)
