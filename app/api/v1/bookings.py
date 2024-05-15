from app.common.dependencies.api_args.bookings import BookingsFiltersDep
from app.common.dependencies.repositories.booking import BookingRepoDep
from app.common.exceptions.api.not_found import ApiNotFoundError
from app.common.exceptions.api.type_error import ApiTypeError
from app.common.exceptions.repositories.booking import BookingNotFoundError, BookingTypeError
from app.common.schemas.booking import BookingSchema
from fastapi import APIRouter

router = APIRouter(prefix="/bookings", tags=["bookings"])
model_name = "Booking"


@router.get("/")
async def get_bookings(raw_filters: BookingsFiltersDep, booking_repo: BookingRepoDep):
    try:
        bookings = await booking_repo.get_objects(raw_filters=raw_filters)
    except BookingTypeError:
        raise ApiTypeError(model_name=model_name, detail=raw_filters.model_dump())
    return bookings


@router.get("/{booking_id}")
async def get_booking(booking_id: int, booking_repo: BookingRepoDep):
    try:
        booking = await booking_repo.get_object(object_id=booking_id)
    except BookingNotFoundError:
        # TODO: logger, sentry etc
        raise ApiNotFoundError(model_name=model_name, detail=dict(booking_id=booking_id))

    # TODO: to_api_model().with_wrapper() ???
    return booking


@router.post("/")
async def create_booking(booking: BookingSchema):
    pass
