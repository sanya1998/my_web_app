import pytest
from app.common.schemas.user import UserBaseReadSchema
from starlette import status
from tests.common import TestClient
from tests.conftest import sign_in
from tests.constants.urls import USERS_CURRENT_URL, USERS_SIGN_OUT_URL, USERS_SIGN_UP_URL, USERS_URL
from tests.constants.users_info import USER_EMAIL


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("cat@dog.com", "easy_password", status.HTTP_201_CREATED),
        ("cat@dog.com", "easy_password", status.HTTP_409_CONFLICT),
        ("bad_email", "easy_password", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
async def test_sign_up(client: TestClient, email, password, status_code):
    await client.post(
        url=USERS_SIGN_UP_URL,
        code=status_code,
        data={"email": email, "password": password},
    )


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("fedor@moloko.ru", "wrong_password", status.HTTP_401_UNAUTHORIZED),
        ("fedor@moloko.ru", "hard_password", status.HTTP_200_OK),
        ("no-person@moloko.ru", "hard_password", status.HTTP_404_NOT_FOUND),
    ],
)
async def test_sign_in(client: TestClient, email, password, status_code):
    await sign_in(client=client, email=email, password=password, code=status_code)


async def test_current_user(user_client: TestClient):
    # Получить данные о текущем пользователе
    user = await user_client.get(USERS_CURRENT_URL, model=UserBaseReadSchema)
    assert user.email == USER_EMAIL

    # Выйти
    await user_client.post(USERS_SIGN_OUT_URL)

    # Нет доступа для неавторизованного пользователя
    await user_client.get(USERS_CURRENT_URL, code=status.HTTP_401_UNAUTHORIZED)


async def test_get_users(admin_client: TestClient):
    await admin_client.get(USERS_URL)
