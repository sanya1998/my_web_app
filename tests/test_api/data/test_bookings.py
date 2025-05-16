from datetime import date
from typing import List

import pytest
from app.common.constants.roles import BookingsRecipientRoleEnum
from app.common.schemas.booking import BookingBaseReadSchema, BookingReadSchema, CurrentUserBookingReadSchema
from app.common.schemas.room import ManyRoomsReadSchema
from app.common.schemas.user import UserBaseReadSchema
from app.dependencies.input import BookingCreateInputSchema, BookingUpdateInputSchema
from httpx import QueryParams
from starlette import status
from tests.common import TestClient
from tests.constants.urls import BOOKINGS_URL, ROOMS_URL, USERS_CURRENT_URL


@pytest.mark.parametrize(
    "data, status_code",
    [
        (
            dict(date_from=date(2024, 11, 7), date_to=date(2024, 11, 8), room_id=7),
            status.HTTP_401_UNAUTHORIZED,
        ),
    ],
)
async def test_unauthorized_create_bookings(client: TestClient, mock_send_email, data, status_code):
    """Неавторизованный пользователь не может бронировать"""
    await client.post(BOOKINGS_URL, code=status_code, data=data)


@pytest.mark.parametrize(
    "data, status_code",
    [
        (dict(date_from=date(2024, 11, 7), room_id=7), status.HTTP_422_UNPROCESSABLE_ENTITY),
        (dict(date_to=date(2024, 11, 8), room_id=7), status.HTTP_422_UNPROCESSABLE_ENTITY),
        (dict(date_from=date(2024, 11, 7), date_to=date(2024, 11, 8)), status.HTTP_422_UNPROCESSABLE_ENTITY),
    ],
)
async def test_api_not_created_booking(
    user_client: TestClient, manager_client: TestClient, mock_send_email, data, status_code
):
    """Некорректные данные при создании"""
    await user_client.post(BOOKINGS_URL, code=status_code, data=data)


@pytest.mark.parametrize(
    "data, status_code",
    [
        (dict(date_from=date(2024, 11, 7), date_to=date(2024, 11, 8), room_id=7), status.HTTP_201_CREATED),
    ],
)
async def test_api_crud_booking(
    user_client: TestClient, manager_client: TestClient, mock_send_email, data, status_code
):
    # create
    created_booking = await user_client.post(BOOKINGS_URL, code=status_code, model=BookingBaseReadSchema, data=data)
    assert created_booking.id is not None

    # get
    gotten_booking_self = await user_client.get(
        f"{BOOKINGS_URL}{created_booking.id}",
        model=CurrentUserBookingReadSchema,
        params=QueryParams(recipient_role=BookingsRecipientRoleEnum.USER.value),
    )
    assert not hasattr(gotten_booking_self, "user")

    gotten_booking = await manager_client.get(
        f"{BOOKINGS_URL}{created_booking.id}",
        model=BookingReadSchema,
        params=QueryParams(recipient_role=BookingsRecipientRoleEnum.MANAGER.value),
    )
    assert gotten_booking.room.hotel.name is not None
    assert gotten_booking.user is not None

    # update
    data = BookingUpdateInputSchema(date_from=date(2024, 11, 6), date_to=date(2024, 11, 10), price=10000)
    data_json = data.model_dump(mode="json")
    updated_booking = await manager_client.put(
        f"{BOOKINGS_URL}{gotten_booking.id}", model=BookingBaseReadSchema, json=data_json
    )

    # delete
    await manager_client.delete(f"{BOOKINGS_URL}{updated_booking.id}", model=BookingBaseReadSchema)


async def test_busy_bookings(user_client: TestClient, mock_send_email):
    """
    Тест, который показывает, что нельзя забронировать комнату, когда все занято
    """
    check_into = date(2024, 11, 7)
    check_out = date(2024, 11, 8)

    # Поучение доступных комнат
    rooms = await user_client.get(
        ROOMS_URL, params=QueryParams(check_into=check_into, check_out=check_out), model=List[ManyRoomsReadSchema]
    )
    room = rooms[0]

    async def creating_booking(status_code):
        data = BookingCreateInputSchema(date_from=check_into, date_to=check_out, room_id=room.id).model_dump()
        return await user_client.post(
            BOOKINGS_URL,
            data=data,
            code=status_code,
        )

    # Занять все доступные комнаты данного типа в эти даты
    for i in range(room.remain_by_room):
        await creating_booking(status.HTTP_201_CREATED)
    # Убедиться, что теперь нельзя забронировать комнату данного типа в эти даты
    await creating_booking(status.HTTP_409_CONFLICT)


async def test_getting_and_deleting_bookings(user_client: TestClient, manager_client: TestClient):
    user = await user_client.get(USERS_CURRENT_URL, model=UserBaseReadSchema)

    bookings_by_user = await manager_client.get(
        BOOKINGS_URL,
        model=List[BookingReadSchema],
        params=QueryParams(user_id=user.id, recipient_role=BookingsRecipientRoleEnum.MANAGER.value),
    )
    assert bookings_by_user[0].room.hotel.name is not None
    assert bookings_by_user[0].user is not None

    bookings_self = await user_client.get(
        BOOKINGS_URL,
        model=List[CurrentUserBookingReadSchema],
        params=QueryParams(user_id=user.id, recipient_role=BookingsRecipientRoleEnum.USER.value),
    )
    assert not hasattr(bookings_self[0], "user")

    assert set(b.id for b in bookings_self) == set(b.id for b in bookings_by_user)

    # TODO: delete bulk
    for booking_item in bookings_by_user:
        await manager_client.delete(f"{BOOKINGS_URL}{booking_item.id}")

    bookings_self = await user_client.get(
        BOOKINGS_URL,
        model=List[CurrentUserBookingReadSchema],
        params=QueryParams(recipient_role=BookingsRecipientRoleEnum.USER.value),
    )
    assert len(bookings_self) == 0
