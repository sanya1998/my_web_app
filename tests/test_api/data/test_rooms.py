from datetime import date

import pytest
from app.common.schemas.room import ManyRoomsReadSchema, RoomReadSchema
from httpx import QueryParams
from starlette import status
from tests.constants import BASE_ROOMS_URL


@pytest.mark.parametrize(
    "params, status_code",
    [
        ({"check_into": date(2024, 11, 13), "check_out": date(2024, 11, 14)}, status.HTTP_200_OK),
        ({}, status.HTTP_200_OK),
    ],
)
async def test_get_by_check_dates(client, params, status_code):
    response = await client.get(BASE_ROOMS_URL, params=QueryParams(**params))
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "params, id_",
    [
        ({"name": "2-комнатный люкс комфорт"}, 6),
        ({"price__gt": 15000, "price__lt": 16000}, 10),
        ({"limit": 1, "offset": 2, "order_by": "id"}, 3),
        ({"limit": 2, "offset": 2, "order_by": "-id"}, 8),
        ({"hotel_id": 6}, 11),
        ({"hotel_name": "Bridge Resort"}, 11),
    ],
)
async def test_get_by_params(client, params, id_):
    response = await client.get(BASE_ROOMS_URL, params=QueryParams(**params))
    assert response.status_code == status.HTTP_200_OK
    assert id_ in set(ManyRoomsReadSchema.model_validate(r).id for r in response.json())


@pytest.mark.parametrize(
    "id_, name, price",
    [
        (1, "Улучшенный с террасой и видом на озеро", 24500),
        (2, "Делюкс Плюс", 24450),
    ],
)
async def test_get_room(client, id_, name, price):
    response = await client.get(f"{BASE_ROOMS_URL}{id_}")
    assert response.status_code == status.HTTP_200_OK
    room = RoomReadSchema.model_validate(response.json())
    assert room.name == name
    assert room.price == price
