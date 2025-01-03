from httpx import AsyncClient
from starlette import status
from tests.constants import BASE_SRV_URL


async def test_ping(client: AsyncClient):
    response = await client.get(f"{BASE_SRV_URL}ping")
    assert response.status_code == status.HTTP_200_OK
