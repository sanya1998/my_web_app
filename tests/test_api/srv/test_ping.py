from httpx import AsyncClient
from starlette import status
from tests.constants.urls import PING_V1_URL


async def test_ping(client: AsyncClient):
    response = await client.get(PING_V1_URL)
    assert response.status_code == status.HTTP_200_OK
