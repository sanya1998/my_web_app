from tests.common import TestClient
from tests.constants.urls import PING_V1_URL


async def test_ping(client: TestClient):
    await client.get(PING_V1_URL)
