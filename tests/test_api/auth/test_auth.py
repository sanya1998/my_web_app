import pytest
from app.common.helpers.response import TokenResponse
from app.exceptions.api import NotFoundApiError, UnauthorizedApiError
from starlette import status
from tests.common import TestClient
from tests.conftest import sign_in
from tests.constants.urls import AUTH_SIGN_UP_URL


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
        url=AUTH_SIGN_UP_URL,
        code=status_code,
        data={"username": email, "password": password},
    )


@pytest.mark.parametrize(
    "email, password, status_code, response_body",
    [
        ("fedor@moloko.ru", "wrong_password", status.HTTP_401_UNAUTHORIZED, UnauthorizedApiError.detail),
        ("no-person@moloko.ru", "hard_password", status.HTTP_404_NOT_FOUND, NotFoundApiError.detail),
    ],
)
async def test_bad_sign_in(client: TestClient, email, password, status_code, response_body):
    response = await sign_in(client=client, email=email, password=password, code=status_code)
    assert response.json() == response_body.model_dump()


@pytest.mark.parametrize(
    "email, password",
    [
        ("fedor@moloko.ru", "hard_password"),
    ],
)
async def test_sign_in(client: TestClient, email, password):
    response = await sign_in(client=client, email=email, password=password)
    token_response = TokenResponse.model_validate(response.json())
    assert token_response.access_token
