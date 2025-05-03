from datetime import date

import pytest
from app.common.constants.roles import BookingsRecipientRoleEnum
from app.common.schemas.booking import BookingBaseReadSchema, BookingReadSchema, CurrentUserBookingReadSchema
from app.common.schemas.room import ManyRoomsReadSchema
from app.common.schemas.user import UserBaseReadSchema
from httpx import AsyncClient, QueryParams
from starlette import status
from tests.constants import BASE_BOOKINGS_URL, BASE_ROOMS_URL, BASE_USERS_URL


async def test_unauthorized_create_bookings(client: AsyncClient, mock_send_email):
    """Неавторизованный пользователь не может бронировать"""
    response = await client.post(
        BASE_BOOKINGS_URL,
        data=dict(
            date_from=date(2024, 11, 7),
            date_to=date(2024, 11, 8),
            room_id=7,
        ),
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    "data, status_code",
    [
        (dict(date_from=date(2024, 11, 7), room_id=7), status.HTTP_422_UNPROCESSABLE_ENTITY),
        (dict(date_to=date(2024, 11, 8), room_id=7), status.HTTP_422_UNPROCESSABLE_ENTITY),
        (dict(date_from=date(2024, 11, 7), date_to=date(2024, 11, 8)), status.HTTP_422_UNPROCESSABLE_ENTITY),
        (dict(date_from=date(2024, 11, 7), date_to=date(2024, 11, 8), room_id=7), status.HTTP_200_OK),
    ],
)
async def test_api_crud_booking(
    user_client: AsyncClient, manager_client: AsyncClient, mock_send_email, data, status_code
):
    response = await user_client.post(BASE_BOOKINGS_URL, data=data)
    assert response.status_code == status_code
    if response.status_code != status.HTTP_200_OK:
        return

    created_booking = BookingBaseReadSchema.model_validate(response.json())
    assert created_booking.id is not None

    # get
    got_response = await user_client.get(
        f"{BASE_BOOKINGS_URL}{created_booking.id}",
        params=QueryParams(recipient_role=BookingsRecipientRoleEnum.USER.value),
    )
    gotten_booking_self = CurrentUserBookingReadSchema.model_validate(got_response.json())
    assert got_response.status_code == status.HTTP_200_OK
    assert not hasattr(gotten_booking_self, "user")

    got_response = await manager_client.get(
        f"{BASE_BOOKINGS_URL}{created_booking.id}",
        params=QueryParams(recipient_role=BookingsRecipientRoleEnum.MANAGER.value),
    )
    gotten_booking = BookingReadSchema.model_validate(got_response.json())
    assert got_response.status_code == status.HTTP_200_OK
    assert gotten_booking.room.hotel.name is not None
    assert gotten_booking.user is not None

    # update
    updated_response = await manager_client.put(
        f"{BASE_BOOKINGS_URL}{gotten_booking.id}",
        data=dict(date_from=date(2024, 11, 6), date_to=date(2024, 11, 10), price=10000),
    )
    updated_booking = BookingBaseReadSchema.model_validate(updated_response.json())
    assert updated_response.status_code == status.HTTP_200_OK

    # delete
    deleted_response = await manager_client.delete(f"{BASE_BOOKINGS_URL}{updated_booking.id}")
    _ = BookingBaseReadSchema.model_validate(deleted_response.json())
    assert deleted_response.status_code == status.HTTP_200_OK


async def test_busy_bookings(user_client: AsyncClient, mock_send_email):
    """
    Тест, который показывает, что нельзя забронировать комнату, когда все занято
    """
    check_into = date(2024, 11, 7)
    check_out = date(2024, 11, 8)

    # Поучение доступных комнат
    response = await user_client.get(
        url=BASE_ROOMS_URL,
        params=QueryParams(
            check_into=check_into,
            check_out=check_out,
        ),
    )
    assert response.status_code == status.HTTP_200_OK
    rooms = [ManyRoomsReadSchema.model_validate(room) for room in response.json()]
    room = rooms[0]

    async def creating_booking():
        return await user_client.post(
            BASE_BOOKINGS_URL,
            data=dict(
                date_from=check_into,
                date_to=check_out,
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


async def test_getting_and_deleting_bookings(user_client: AsyncClient, manager_client: AsyncClient):
    response_user = await user_client.get(f"{BASE_USERS_URL}current")  # TODO: in constants
    user = UserBaseReadSchema.model_validate(response_user.json())

    bookings_by_user_response = await manager_client.get(
        BASE_BOOKINGS_URL, params=QueryParams(user_id=user.id, recipient_role=BookingsRecipientRoleEnum.MANAGER.value)
    )
    assert bookings_by_user_response.status_code == status.HTTP_200_OK
    bookings_by_user = [BookingReadSchema.model_validate(b) for b in bookings_by_user_response.json()]
    assert bookings_by_user[0].room.hotel.name is not None
    assert bookings_by_user[0].user is not None

    bookings_self_response = await user_client.get(
        BASE_BOOKINGS_URL, params=QueryParams(user_id=user.id, recipient_role=BookingsRecipientRoleEnum.USER.value)
    )
    assert bookings_self_response.status_code == status.HTTP_200_OK
    bookings_self = [CurrentUserBookingReadSchema.model_validate(b) for b in bookings_self_response.json()]
    assert not hasattr(bookings_self[0], "user")

    assert set(b.id for b in bookings_self) == set(b.id for b in bookings_by_user)

    for booking_json in bookings_by_user:
        booking = BookingReadSchema.model_validate(booking_json)
        response_delete = await manager_client.delete(f"{BASE_BOOKINGS_URL}{booking.id}")
        assert response_delete.status_code == status.HTTP_200_OK

    bookings_self_response = await user_client.get(
        BASE_BOOKINGS_URL, params=QueryParams(recipient_role=BookingsRecipientRoleEnum.USER.value)
    )
    bookings_self = [CurrentUserBookingReadSchema.model_validate(b) for b in bookings_self_response.json()]
    assert len(bookings_self) == 0
