from typing import List

from app.common.dependencies.api_args.bookings import BookingsFiltersDep
from app.common.dependencies.repositories.booking import BookingRepoDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.not_found import ApiNotFoundError
from app.common.exceptions.api.type_error import ApiTypeError
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.not_found import RepoNotFoundError
from app.common.exceptions.repositories.type_error import RepoTypeError
from app.common.schemas.booking import BookingSchema
from fastapi import APIRouter

router = APIRouter(prefix="/bookings", tags=["bookings"])
model_name = "Booking"


@router.get("/")
async def get_bookings(raw_filters: BookingsFiltersDep, booking_repo: BookingRepoDep) -> List[BookingSchema]:
    try:
        bookings = await booking_repo.get_objects(raw_filters=raw_filters)
    except RepoTypeError as e:
        raise ApiTypeError(e)
    except BaseRepoError as e:
        raise BaseApiError(e)
    return bookings


@router.get("/{booking_id}")
async def get_booking(booking_id: int, booking_repo: BookingRepoDep) -> BookingSchema:
    try:
        booking = await booking_repo.get_object(object_id=booking_id)
    except RepoNotFoundError as e:
        # TODO: logger, sentry etc
        raise ApiNotFoundError(e)
    except BaseRepoError as e:
        raise BaseApiError(e)

    # TODO: to_api_model().with_wrapper() ???
    return booking


@router.post("/")
async def create_booking(booking: BookingSchema):
    pass
