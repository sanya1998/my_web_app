from datetime import date

from app.common.schemas.room import ManyRoomsReadSchema
from app.common.schemas.user import OneUserReadSchema
from httpx import AsyncClient, QueryParams
from starlette import status


async def test_create_bookings(client: AsyncClient):
    """Неавторизованный пользователь не может бронировать"""
    response = await client.post(
        "api/v1/bookings/for_current_user",
        data=dict(
            date_from=date(2024, 11, 7),
            date_to=date(2024, 11, 8),
            room_id=7,
        ),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_busy_bookings(user: OneUserReadSchema, client: AsyncClient):
    """
    Тест, который показывает, что нельзя забронировать комнату, когда все занято
    """
    date_from = date(2024, 11, 7)
    date_to = date(2024, 11, 8)

    # Поучение доступных комнат
    response = await client.get(
        "api/v1/rooms/",
        params=QueryParams(
            date_from=date_from,
            date_to=date_to,
        ),
    )
    assert response.status_code == status.HTTP_200_OK
    rooms = [ManyRoomsReadSchema.model_validate(room) for room in response.json()]

    room = rooms[0]

    async def creating_booking():
        return await client.post(
            "api/v1/bookings/for_current_user",
            data=dict(
                date_from=date_from,
                date_to=date_to,
                room_id=room.id,
            ),
        )

    # Занять все доступные комнаты данного типа в эти даты
    for i in range(room.remain_by_room):
        response = await creating_booking()
        assert response.status_code == status.HTTP_200_OK
    # Убедиться, что теперь нельзя забронировать комнату данного типа в эти даты
    response = await creating_booking()
    assert response.status_code == status.HTTP_409_CONFLICT
