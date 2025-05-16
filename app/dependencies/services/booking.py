from typing import Annotated

from app.dependencies.repositories import BookingRepoDep, RoomRepoDep
from app.services import BookingService
from fastapi import Depends


# TODO: Мб инициализировать только session: PostgresSessionDep, а возвращать return get_booking_repo(session) ?
def get_booking_service(booking_repo: BookingRepoDep, room_repo: RoomRepoDep):
    return BookingService(booking_repo=booking_repo, room_repo=room_repo)


BookingServiceDep = Annotated[BookingService, Depends(get_booking_service)]
