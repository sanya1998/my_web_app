from typing import Annotated, Union

from app.common.constants.info_types import InfoTypes
from app.dependencies.repositories.booking import BookingRepoDep
from app.dependencies.repositories.hotel import HotelRepoDep
from app.dependencies.repositories.room import RoomRepoDep
from app.dependencies.repositories.user import UserRepoDep
from app.repositories import BookingRepo, HotelRepo, RoomRepo, UserRepo
from fastapi import Depends


# TODO: Мб инициализировать только session: PostgresSessionDep, а возвращать return get_hotel_repo(session) ?
def get_chosen_repo(
    info_type: InfoTypes,
    repo_hotel: HotelRepoDep,
    repo_room: RoomRepoDep,
    repo_booking: BookingRepoDep,
    repo_user: UserRepoDep,
):
    match info_type:
        case InfoTypes.HOTELS:
            return repo_hotel
        case InfoTypes.ROOMS:
            return repo_room
        case InfoTypes.BOOKINGS:
            return repo_booking
        case InfoTypes.USERS:
            return repo_user


ChosenRepo = Annotated[Union[HotelRepo, RoomRepo, BookingRepo, UserRepo], Depends(get_chosen_repo)]
