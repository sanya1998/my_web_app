from typing import Annotated

from app.dependencies.db import PostgresSessionAnn
from app.dependencies.repositories.booking import get_booking_repo
from app.dependencies.repositories.room import get_room_repo
from app.services import BookingService
from fastapi import Depends


def get_booking_service(session: PostgresSessionAnn):
    return BookingService(booking_repo=get_booking_repo(session), room_repo=get_room_repo(session))


BookingServiceAnn = Annotated[BookingService, Depends(get_booking_service)]
