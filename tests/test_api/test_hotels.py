from datetime import date

import pytest
from app.common.schemas.hotel import ManyHotelsReadSchema
from httpx import QueryParams
from starlette import status

BASE_URL = "/api/v1/hotels/"


@pytest.mark.parametrize(
    "params, status_code",
    [
        ({"date_from": date(2024, 11, 13), "date_to": date(2024, 11, 14)}, status.HTTP_200_OK),
        ({"date_from": date(2024, 11, 13), "date_to": date(2025, 1, 14)}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ({"date_from": date(2024, 11, 15), "date_to": date(2024, 11, 14)}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
async def test_get_hotels(client, params, status_code):
    response = await client.get(BASE_URL, params=QueryParams(**params))
    assert response.status_code == status_code


async def test_get_hotels_without_dates(client):
    response = await client.get(BASE_URL)
    assert response.status_code == status.HTTP_200_OK
    hotels = [ManyHotelsReadSchema.model_validate(h) for h in response.json()]
    # Без дат нельзя посчитать, сколько свободных комнат осталось
    assert hotels[0].remain_by_hotel is None
