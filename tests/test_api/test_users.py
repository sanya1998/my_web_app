import pytest
from app.common.schemas.user import OneUserReadSchema
from httpx import AsyncClient
from starlette import status

BASE_URL = "/api/v1/users/"


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
        url=f"{BASE_URL}sign_up",
        data={"email": email, "raw_password": password},
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
    response = await client.post(
        url=f"{BASE_URL}sign_in",
        data={"email": email, "raw_password": password},
    )
    assert response.status_code == status_code


async def test_get_users(admin_user: OneUserReadSchema, client: AsyncClient):
    response = await client.get(f"{BASE_URL}for_admin")
    assert response.status_code == status.HTTP_200_OK
