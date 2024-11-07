from httpx import AsyncClient
from starlette import status


async def test_ping(client: AsyncClient):
    response = await client.get("/ping")
    assert response.status_code == status.HTTP_200_OK
