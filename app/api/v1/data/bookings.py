from typing import List

from app.common.dependencies.api_args.bookings import BookingsFiltersDep
from app.common.dependencies.repositories.booking import BookingRepoDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.not_found import NotFoundApiError
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.schemas.booking import BookingSchema
from fastapi import APIRouter

router = APIRouter(prefix="/bookings", tags=["bookings"])
model_name = "Booking"


@router.get("/")
async def get_bookings(raw_filters: BookingsFiltersDep, booking_repo: BookingRepoDep) -> List[BookingSchema]:
    try:
        bookings = await booking_repo.get_objects(raw_filters=raw_filters)
    except BaseRepoError:
        raise BaseApiError
    return bookings


@router.get("/{booking_id}")
async def get_booking(booking_id: int, booking_repo: BookingRepoDep) -> BookingSchema:
    try:
        booking = await booking_repo.get_object(id=booking_id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except BaseRepoError:  # TODO: Можно ли базовое исключение наложить на все ручки сразу?
        raise BaseApiError
    # TODO: to_api_model().with_wrapper() ??? (видел в другом проекте. понять: зачем это)
    return booking


@router.post("/")
async def create_booking(booking: BookingSchema):
    pass
