from datetime import date
from typing import List

import pytest
from app.common.schemas.hotel import HotelBaseReadSchema, HotelReadSchema, ManyHotelsReadSchema
from app.common.schemas.room import ManyRoomsReadSchema
from httpx import QueryParams
from starlette import status
from tests.constants.urls import HOTELS_URL, ROOMS_URL


@pytest.mark.parametrize(
    "data, status_code",
    [
        ({"name": "hotel_name4"}, status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
async def test_no_created_hotel(moderator_client, data, status_code):
    """Некорректные входные данные"""
    await moderator_client.post(HOTELS_URL, code=status_code, data=data)


@pytest.mark.parametrize(
    "data, status_code",
    [
        ({"name": "name1", "location": "big city", "stars": 1}, status.HTTP_201_CREATED),
        ({"name": "name2", "location": "big city", "stars": 2, "services": ["Swimming pool"]}, status.HTTP_201_CREATED),
        ({"name": "name3", "location": "big city", "image_id": 8}, status.HTTP_201_CREATED),
    ],
)
async def test_crud_hotel(moderator_client, data, status_code):
    # create
    created_hotel = await moderator_client.post(HOTELS_URL, code=status_code, model=HotelBaseReadSchema, data=data)
    assert created_hotel.id is not None

    # patch
    new_name, new_location = f"patched {created_hotel.name}", f"patched {created_hotel.location}"
    await moderator_client.patch(
        f"{HOTELS_URL}{created_hotel.id}",
        model=HotelBaseReadSchema,
        json=dict(name=new_name, location=new_location),
    )
    # get
    gotten_patched_hotel = await moderator_client.get(f"{HOTELS_URL}{created_hotel.id}", model=HotelReadSchema)
    assert gotten_patched_hotel.name == new_name and gotten_patched_hotel.location == new_location
    assert gotten_patched_hotel.stars == created_hotel.stars and gotten_patched_hotel.services == created_hotel.services

    # update
    new_name, new_location = f"updated {created_hotel.name}", f"updated {created_hotel.location}"
    await moderator_client.put(
        f"{HOTELS_URL}{created_hotel.id}",
        model=HotelBaseReadSchema,
        json=dict(name=new_name, location=new_location),
    )
    # get
    gotten_put_hotel = await moderator_client.get(f"{HOTELS_URL}{created_hotel.id}", model=HotelReadSchema)
    assert gotten_put_hotel.name == new_name and gotten_put_hotel.location == new_location
    # Так как в put ручку не передавались поля `stars` и `services`, то после обновления их значения станут по умолчанию
    assert gotten_put_hotel.stars is None and gotten_put_hotel.services == []

    # delete
    await moderator_client.delete(f"{HOTELS_URL}{created_hotel.id}", model=HotelBaseReadSchema)


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
    await client.get(HOTELS_URL, params=QueryParams(**params), code=status_code)


async def test_get_hotels_without_dates(client):
    hotels = await client.get(HOTELS_URL, model=List[ManyHotelsReadSchema])

    rooms = await client.get(
        ROOMS_URL, model=List[ManyRoomsReadSchema], params=QueryParams(hotel_id=hotels[0].id, limit=100)
    )

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
    """Проверка, что определенный отель находится в результате при определенных фильтрах"""
    hotels = await client.get(HOTELS_URL, model=List[ManyHotelsReadSchema], params=QueryParams(**params))
    assert id_ in set(h.id for h in hotels)
