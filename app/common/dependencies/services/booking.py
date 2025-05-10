from typing import Annotated

from app.common.dependencies.repositories import BookingRepoDep, RoomRepoDep
from app.common.exceptions.api import BaseApiError
from app.common.exceptions.services import BaseServiceError
from app.services import BookingService
from fastapi import Depends


def get_booking_service(booking_repo: BookingRepoDep, room_repo: RoomRepoDep):
    try:
        return BookingService(booking_repo=booking_repo, room_repo=room_repo)
    except BaseServiceError:
        raise BaseApiError


BookingServiceDep = Annotated[BookingService, Depends(get_booking_service)]
