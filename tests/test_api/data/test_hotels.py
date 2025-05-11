from datetime import date

import pytest
from app.common.schemas.hotel import HotelBaseReadSchema, HotelReadSchema, ManyHotelsReadSchema
from app.common.schemas.room import ManyRoomsReadSchema
from httpx import QueryParams
from starlette import status
from tests.constants.urls import HOTELS_URL, ROOMS_URL


@pytest.mark.parametrize(
    "data, status_code",
    [
        ({"name": "hotel_name1", "location": "big city"}, status.HTTP_200_OK),
        ({"name": "hotel_name2", "location": "big city", "services": ["Тренажёрный зал"]}, status.HTTP_200_OK),
        ({"name": "hotel_name3", "location": "big city", "image_id": 8}, status.HTTP_200_OK),
        ({"name": "hotel_name4"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
async def test_crud_hotel(moderator_client, data, status_code):
    response = await moderator_client.post(HOTELS_URL, data=data)
    assert response.status_code == status_code
    if response.status_code != status.HTTP_200_OK:
        return

    hotel = HotelBaseReadSchema.model_validate(response.json())
    assert hotel.id is not None

    # get
    got_response = await moderator_client.get(f"{HOTELS_URL}{hotel.id}")
    _ = HotelReadSchema.model_validate(got_response.json())
    assert got_response.status_code == status.HTTP_200_OK

    # update
    updated_response = await moderator_client.put(
        f"{HOTELS_URL}{hotel.id}",
        data=dict(name=f"updated_{hotel.name}", location=f"updated_{hotel.location}"),
    )
    _ = HotelBaseReadSchema.model_validate(updated_response.json())
    assert updated_response.status_code == status.HTTP_200_OK

    # delete
    deleted_response = await moderator_client.delete(f"{HOTELS_URL}{hotel.id}")
    _ = HotelBaseReadSchema.model_validate(deleted_response.json())
    assert deleted_response.status_code == status.HTTP_200_OK


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
    response = await client.get(HOTELS_URL, params=QueryParams(**params))
    assert response.status_code == status_code


async def test_get_hotels_without_dates(client):
    response_hotels = await client.get(HOTELS_URL)
    assert response_hotels.status_code == status.HTTP_200_OK
    hotels = [ManyHotelsReadSchema.model_validate(h) for h in response_hotels.json()]

    response_rooms = await client.get(ROOMS_URL, params=QueryParams(hotel_id=hotels[0].id, limit=100))
    rooms = [ManyRoomsReadSchema.model_validate(r) for r in response_rooms.json()]

    # Без дат нельзя посчитать, сколько свободных комнат осталось, поэтому remain_by_hotel = суммарное количество
    assert hotels[0].remain_by_hotel == sum([r.remain_by_room for r in rooms]) == sum([r.quantity for r in rooms])


@pytest.mark.parametrize(
    "params, id_",
    [
        ({"location__ilike": "РЕСПУБЛИКА Алтай, +точный АДРЕС"}, 1),
        ({"location": "Адрес Skala"}, 2),
        ({"rooms_price__lt": 5000}, 4),
        ({"name": "Palace"}, 5),
        ({"search": "bridge"}, 6),
        ({"search": "район"}, 3),
        ({"services__contains": "SPA"}, 5),
    ],
)
async def test_hotels_params(client, params, id_):
    response = await client.get(HOTELS_URL, params=QueryParams(**params))
    assert response.status_code == status.HTTP_200_OK
    assert id_ in set(ManyHotelsReadSchema.model_validate(r).id for r in response.json())
