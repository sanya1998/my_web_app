import pytest
from app.common.constants.srv import PING_V1, PING_V2
from httpx import AsyncClient
from starlette import status
from tests.constants import BASE_SRV_URL_V1, BASE_SRV_URL_V2


@pytest.mark.parametrize(
    "url, answer",
    [
        (BASE_SRV_URL_V1, PING_V1),
        (BASE_SRV_URL_V2, PING_V2),
    ],
)
async def test_versioning(client: AsyncClient, url, answer):
    response = await client.get(f"{url}ping")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == answer
