from fastapi import APIRouter

from app.common.api_models.booking import SBooking
from app.common.dependencies.repositories.booking import BookingRepoDep
from app.common.exceptions.api.not_found import ApiNotFound
from app.common.exceptions.repositories.booking import BookingNotFound

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/")
async def get_bookings(filters, booking_repo: BookingRepoDep):
    bookings = await booking_repo.get_objects(filters=filters)
    return bookings


@router.get("/{booking_id}")
async def get_booking(booking_id: int, booking_repo: BookingRepoDep):
    try:
        booking = await booking_repo.get_object(object_id=booking_id)
    except BookingNotFound:
        # TODO: logger, sentry etc
        raise ApiNotFound(model_name="Booking", detail=dict(booking_id=booking_id))

    # TODO: to_api_model().with_wrapper() ???
    return booking


@router.post("/")
async def create_booking(booking: SBooking):
    pass
