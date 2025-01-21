from httpx import AsyncClient
from starlette import status
from tests.constants import BASE_SRV_URL_V1


async def test_ping(client: AsyncClient):
    response = await client.get(f"{BASE_SRV_URL_V1}ping")
    assert response.status_code == status.HTTP_200_OK
