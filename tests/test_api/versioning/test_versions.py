import pytest
from httpx import AsyncClient
from starlette import status
from tests.constants import BASE_SRV_URL_V1, BASE_SRV_URL_V2


@pytest.mark.parametrize(
    "url, answer",
    [
        (BASE_SRV_URL_V1, {"api_version": 1, "success": True}),
        (BASE_SRV_URL_V2, {"api_version": 2, "success": True}),
    ],
)
async def test_versioning(client: AsyncClient, url, answer):
    response = await client.get(f"{url}ping")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == answer
