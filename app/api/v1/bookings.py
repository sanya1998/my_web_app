from fastapi import APIRouter
from sqlalchemy import select

from app.common.dependencies.db.db import SessionDep
from app.common.dependencies.repositories.booking import BookingRepoDep
from app.common.exceptions.api.not_found import ApiNotFound
from app.common.exceptions.repositories.booking import BookingNotFound
from app.common.models.booking import SBooking
from app.common.tables import Bookings

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/")
async def get_bookings(session: SessionDep):
    # Плохой вариант
    query = select(Bookings)
    result = await session.execute(query)
    bookings = result.scalars().all()
    return bookings


@router.get("/{booking_id}")
async def get_booking(booking_id: int, booking_repo: BookingRepoDep):
    # Хороший вариант
    try:
        booking = await booking_repo.get_object(object_id=booking_id)
    except BookingNotFound as e:
        # TODO: logger, sentry etc
        raise ApiNotFound(model_name="Booking", detail=dict(booking_id=booking_id))

    # TODO: to_api_model().with_wrapper() ???
    return booking


@router.post("/")
async def create_booking(booking: SBooking):
    pass
