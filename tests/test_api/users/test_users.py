import pytest
from app.common.schemas.user import UserBaseReadSchema
from httpx import AsyncClient
from starlette import status
from tests.conftest import sign_in
from tests.constants import BASE_USERS_URL


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("cat@dog.com", "easy_password", status.HTTP_200_OK),
        ("cat@dog.com", "easy_password", status.HTTP_409_CONFLICT),
        ("email", "easy_password", status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
async def test_sign_up(client: AsyncClient, email, password, status_code):
    response = await client.post(
        url=f"{BASE_USERS_URL}sign_up",
        data={"email": email, "password": password},
    )
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("fedor@moloko.ru", "wrong_password", status.HTTP_401_UNAUTHORIZED),
        ("fedor@moloko.ru", "hard_password", status.HTTP_200_OK),
        ("no-person@moloko.ru", "hard_password", status.HTTP_404_NOT_FOUND),
    ],
)
async def test_sign_in(client: AsyncClient, email, password, status_code):
    await sign_in(client=client, email=email, password=password, expected_status=status_code)


async def test_current_user(user_client: AsyncClient):
    response_user = await user_client.get(f"{BASE_USERS_URL}current")
    user = UserBaseReadSchema.model_validate(response_user.json())
    assert response_user.status_code == status.HTTP_200_OK
    assert user.email == "sharik@moloko.ru"

    response_sign_out = await user_client.post(f"{BASE_USERS_URL}sign_out")
    assert response_sign_out.status_code == 200

    response_user = await user_client.get(f"{BASE_USERS_URL}current")
    assert response_user.status_code == status.HTTP_401_UNAUTHORIZED


async def test_get_users(admin_client: AsyncClient):
    response = await admin_client.get(BASE_USERS_URL)
    assert response.status_code == status.HTTP_200_OK
