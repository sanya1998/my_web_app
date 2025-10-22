from tests.common import CustomAsyncClient
from tests.constants.urls import PING_V1_URL


async def test_ping(client: CustomAsyncClient):
    await client.get(PING_V1_URL)
