from datetime import date

import pytest
from app.common.schemas.hotel import ManyHotelsReadSchema
from app.common.schemas.room import ManyRoomsReadSchema
from httpx import QueryParams
from starlette import status

BASE_URL = "/api/v1/hotels/"


@pytest.mark.parametrize(
    "params, status_code",
    [
        ({"rooms_check_into": date(2024, 11, 13), "rooms_check_out": date(2024, 11, 14)}, status.HTTP_200_OK),
        (
            {"rooms_check_into": date(2024, 11, 13), "rooms_check_out": date(2025, 1, 14)},
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
        (
            {"rooms_check_into": date(2024, 11, 15), "rooms_check_out": date(2024, 11, 14)},
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ),
    ],
)
async def test_get_hotels(client, params, status_code):
    response = await client.get(BASE_URL, params=QueryParams(**params))
    assert response.status_code == status_code


async def test_get_hotels_without_dates(client):
    response_hotels = await client.get(BASE_URL)
    assert response_hotels.status_code == status.HTTP_200_OK
    hotels = [ManyHotelsReadSchema.model_validate(h) for h in response_hotels.json()]

    response_rooms = await client.get("/api/v1/rooms/", params=QueryParams(hotel_id=hotels[0].id, limit=100))
    rooms = [ManyRoomsReadSchema.model_validate(r) for r in response_rooms.json()]

    # Без дат нельзя посчитать, сколько свободных комнат осталось, поэтому remain_by_hotel = суммарное количество
    assert hotels[0].remain_by_hotel == sum([r.remain_by_room for r in rooms]) == sum([r.quantity for r in rooms])
