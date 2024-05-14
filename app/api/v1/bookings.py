from app.common.dependencies.filters.bookings import BookingsFiltersDep
from app.common.dependencies.repositories.booking import BookingRepoDep
from app.common.exceptions.api.not_found import ApiNotFoundError
from app.common.exceptions.repositories.booking import BookingNotFoundErrorError
from app.common.schemas.booking import BookingSchema
from fastapi import APIRouter

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/")
async def get_bookings(raw_filters: BookingsFiltersDep, booking_repo: BookingRepoDep):  # TODO: limit: int, offset: int
    bookings = await booking_repo.get_objects(raw_filters=raw_filters)
    return bookings


@router.get("/{booking_id}")
async def get_booking(booking_id: int, booking_repo: BookingRepoDep):
    try:
        booking = await booking_repo.get_object(object_id=booking_id)
    except BookingNotFoundErrorError:
        # TODO: logger, sentry etc
        raise ApiNotFoundError(model_name="Booking", detail=dict(booking_id=booking_id))

    # TODO: to_api_model().with_wrapper() ???
    return booking


@router.post("/")
async def create_booking(booking: BookingSchema):
    pass
