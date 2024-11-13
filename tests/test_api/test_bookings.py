from datetime import date

from app.common.schemas.booking import ManyBookingsReadSchema
from app.common.schemas.room import ManyRoomsReadSchema
from app.common.schemas.user import OneUserReadSchema
from httpx import AsyncClient, QueryParams
from starlette import status

BASE_BOOKINGS_URL = "/api/v1/bookings/"


async def test_create_bookings(client: AsyncClient):
    """Неавторизованный пользователь не может бронировать"""
    response = await client.post(
        f"{BASE_BOOKINGS_URL}for_current_user",
        data=dict(
            date_from=date(2024, 11, 7),
            date_to=date(2024, 11, 8),
            room_id=7,
        ),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


async def test_busy_bookings(user_client: AsyncClient):
    """
    Тест, который показывает, что нельзя забронировать комнату, когда все занято
    """
    date_from = date(2024, 11, 7)
    date_to = date(2024, 11, 8)

    # Поучение доступных комнат
    response = await user_client.get(
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
        return await user_client.post(
            f"{BASE_BOOKINGS_URL}for_current_user",
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


async def test_delete_bookings(user_client: AsyncClient, manager_client: AsyncClient):
    response_user = await user_client.get("/api/v1/users/current")
    user = OneUserReadSchema.model_validate(response_user.json())

    bookings_by_id_response = await manager_client.get(
        f"{BASE_BOOKINGS_URL}for_manager", params=QueryParams(user_id=user.id)
    )
    bookings_by_id = bookings_by_id_response.json()

    bookings_self_response = await user_client.get(f"{BASE_BOOKINGS_URL}for_current_user")
    bookings_self = bookings_self_response.json()

    assert bookings_self == bookings_by_id

    for booking_json in bookings_by_id:
        booking = ManyBookingsReadSchema.model_validate(booking_json)
        response_delete = await manager_client.delete(f"{BASE_BOOKINGS_URL}{booking.id}/for_manager")
        assert response_delete.status_code == status.HTTP_200_OK

    bookings_self_response = await user_client.get(f"{BASE_BOOKINGS_URL}for_current_user")
    bookings_self = bookings_self_response.json()
    assert len(bookings_self) == 0
