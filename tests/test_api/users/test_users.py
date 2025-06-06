from app.common.schemas.user import UserBaseReadSchema
from starlette import status
from tests.common import TestClient
from tests.constants.urls import AUTH_SIGN_OUT_URL, USERS_CURRENT_URL, USERS_URL
from tests.constants.users_info import USER_EMAIL


async def test_current_user(user_client: TestClient):
    # Получить данные о текущем пользователе
    user = await user_client.get(USERS_CURRENT_URL, model=UserBaseReadSchema)
    assert user.email == USER_EMAIL

    # Выйти
    await user_client.post(AUTH_SIGN_OUT_URL)

    # Нет доступа для неавторизованного пользователя
    await user_client.get(USERS_CURRENT_URL, code=status.HTTP_401_UNAUTHORIZED)


async def test_get_users(admin_client: TestClient):
    await admin_client.get(USERS_URL)
