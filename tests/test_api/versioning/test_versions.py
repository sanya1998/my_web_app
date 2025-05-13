import pytest
from app.common.constants.srv import PING_RESULT_V1, PING_RESULT_V2, PingResult
from tests.common import TestClient
from tests.constants.urls import PING_V1_URL, PING_V2_URL


@pytest.mark.parametrize(
    "url, answer",
    [
        (PING_V1_URL, PING_RESULT_V1),
        (PING_V2_URL, PING_RESULT_V2),
    ],
)
async def test_versioning(client: TestClient, url, answer):
    ping_result = await client.get(url, model=PingResult)
    assert ping_result == answer
