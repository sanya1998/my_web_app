from typing import Annotated, Union

from app.common.constants.info_types import InfoTypes
from app.dependencies.db import PostgresSessionDep
from app.dependencies.repositories.booking import get_booking_repo
from app.dependencies.repositories.hotel import get_hotel_repo
from app.dependencies.repositories.room import get_room_repo
from app.dependencies.repositories.user import get_user_repo
from app.repositories import BookingRepo, HotelRepo, RoomRepo, UserRepo
from fastapi import Depends


def get_chosen_repo(info_type: InfoTypes, session: PostgresSessionDep):
    match info_type:
        case InfoTypes.HOTELS:
            return get_hotel_repo(session)
        case InfoTypes.ROOMS:
            return get_room_repo(session)
        case InfoTypes.BOOKINGS:
            return get_booking_repo(session)
        case InfoTypes.USERS:
            return get_user_repo(session)


ChosenRepo = Annotated[Union[HotelRepo, RoomRepo, BookingRepo, UserRepo], Depends(get_chosen_repo)]
