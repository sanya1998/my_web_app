# TODO: удалить весь файл и связи с ним после того, как будет проведена работа с графаной
import time
from random import random

from app.dependencies.auth.roles.admin import AdminDep
from fastapi import APIRouter

router = APIRouter(prefix="/testing", dependencies=[AdminDep])


@router.get(path="/long")
def long_answer() -> float:
    waiting = random() * 5
    time.sleep(waiting)
    return waiting


@router.get(path="/error")
def get_error():
    if random() > 0.5:
        raise ZeroDivisionError
    else:
        raise KeyError


@router.get(path="/memory")
def memory():
    _ = [i for i in range(10_000_000)]
    return 0


# TODO: сделать OAuth2PasswordBearer SIGN_IN_URL
# TODO: без auto_error=False, вместо user_input: UserInputDep
#  приходится использовать form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
#  user_input = UserInput(username=form_data.username, password=SecretStr(form_data.password))
#  мб как-то добавить заголовок: Authorization: Annotated[str, Header()] = "bearer"
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl=URL_FOR_GETTING_OF_TOKEN)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl=URL_FOR_GETTING_OF_TOKEN, auto_error=False)


# # TODO: не вызывается, если в куках нет поля session
# @router.post(path=f"/token")
# async def login(user_input: UserInputDep, auth_service: AuthorizationServiceDep):
#     access_token = await auth_service.sign_in(user_input)
#     return {"access_token": access_token, "token_type": "bearer"}  # TODO: response_model ORJSONResponse


# @router.post(path=f"/token")
# async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], auth_service: AuthorizationServiceDep):
#     user_input = UserInput(username=form_data.username, password=SecretStr(form_data.password))
#     access_token = await auth_service.sign_in(user_input)
#     return {"access_token": access_token, "token_type": "bearer"}  # TODO: response_model ORJSONResponse
