from datetime import date
from typing import List

import pytest
from app.common.schemas.room import ManyRoomsReadSchema, RoomReadSchema
from httpx import QueryParams
from starlette import status
from tests.common import TestClient
from tests.constants.urls import ROOMS_URL


@pytest.mark.parametrize(
    "params, status_code",
    [
        ({"check_into": date(2024, 11, 13), "check_out": date(2024, 11, 14)}, status.HTTP_200_OK),
        ({}, status.HTTP_200_OK),
    ],
)
async def test_get_by_check_dates(client: TestClient, params: dict, status_code: int):
    await client.get(ROOMS_URL, params=QueryParams(**params))


@pytest.mark.parametrize(
    "params, id_",
    [
        ({"name": "2-комнатный люкс комфорт"}, 6),
        ({"price__gt": 15000, "price__lt": 16000}, 10),
        ({"limit": 1, "offset": 2, "order_by": "id"}, 3),
        ({"limit": 2, "offset": 2, "order_by": "-id"}, 8),
        ({"hotel_id": 6}, 11),
        ({"hotel_name": "Bridge Resort"}, 11),
        ({"order_by": ["price", "id"], "price__gt": 26000, "price__lt": 27000, "limit": 1}, 3),
        ({"order_by": ["price", "-id"], "price__gt": 26000, "price__lt": 27000, "limit": 1}, 11),
    ],
)
async def test_get_by_params(client: TestClient, params: dict, id_: int):
    """Проверка, что определенный тип комнаты находится в результате при определенных фильтрах"""
    rooms = await client.get(ROOMS_URL, model=List[ManyRoomsReadSchema], params=QueryParams(**params))
    assert id_ in set(r.id for r in rooms)


@pytest.mark.parametrize(
    "id_, name, price",
    [
        (1, "Улучшенный с террасой и видом на озеро", 24500),
        (2, "Делюкс Плюс", 24450),
    ],
)
async def test_get_room(client: TestClient, id_: int, name: str, price: int):
    room = await client.get(f"{ROOMS_URL}{id_}", model=RoomReadSchema)
    assert room.name == name
    assert room.price == price
