import pytest
from app.common.constants.srv import PING_RESULT_V1, PING_RESULT_V2
from httpx import AsyncClient
from starlette import status
from tests.constants.urls import PING_V1_URL, PING_V2_URL


@pytest.mark.parametrize(
    "url, answer",
    [
        (PING_V1_URL, PING_RESULT_V1),
        (PING_V2_URL, PING_RESULT_V2),
    ],
)
async def test_versioning(client: AsyncClient, url, answer):
    response = await client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == answer
