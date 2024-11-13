from datetime import date

import pytest
from httpx import QueryParams
from starlette import status


@pytest.mark.parametrize(
    "params, status_code",
    [
        ({"date_from": date(2024, 11, 13), "date_to": date(2024, 11, 14)}, status.HTTP_200_OK),
        ({"date_from": date(2024, 11, 13), "date_to": date(2025, 1, 14)}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"date_from": date(2024, 11, 15), "date_to": date(2024, 11, 14)}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
async def test_get_hotels(client, params, status_code):
    response = await client.get("/api/v1/hotels/", params=QueryParams(**params))
    assert response.status_code == status_code
