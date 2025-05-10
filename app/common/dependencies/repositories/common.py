from typing import Annotated, Union

from app.common.constants.info_types import InfoTypes
from app.common.dependencies.repositories.booking import BookingRepoDep
from app.common.dependencies.repositories.hotel import HotelRepoDep
from app.common.dependencies.repositories.room import RoomRepoDep
from app.common.dependencies.repositories.user import UserRepoDep
from app.common.exceptions.api import BaseApiError
from app.common.exceptions.services import BaseServiceError
from app.repositories import BookingRepo, HotelRepo, RoomRepo, UserRepo
from fastapi import Depends


def get_chosen_repo(
    info_type: InfoTypes,
    repo_hotel: HotelRepoDep,
    repo_room: RoomRepoDep,
    repo_booking: BookingRepoDep,
    repo_user: UserRepoDep,
):
    try:
        match info_type:
            case InfoTypes.HOTELS:
                return repo_hotel
            case InfoTypes.ROOMS:
                return repo_room
            case InfoTypes.BOOKINGS:
                return repo_booking
            case InfoTypes.USERS:
                return repo_user
    except BaseServiceError:
        raise BaseApiError


ChosenRepo = Annotated[Union[HotelRepo, RoomRepo, BookingRepo, UserRepo], Depends(get_chosen_repo)]
