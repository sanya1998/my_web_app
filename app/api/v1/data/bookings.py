from typing import List

from app.common.dependencies.api_args.auth import CurrentUserDep
from app.common.dependencies.api_args.bookings import BookingsFiltersDep
from app.common.dependencies.repositories.booking import BookingRepoDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.multiple_results import MultipleResultsApiError
from app.common.exceptions.api.not_found import NotFoundApiError
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.multiple_results import MultipleResultsRepoError
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.schemas.booking import BookingSchema
from fastapi import APIRouter

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/")
async def get_my_bookings(
    raw_filters: BookingsFiltersDep, user: CurrentUserDep, booking_repo: BookingRepoDep
) -> List[BookingSchema]:
    try:
        bookings = await booking_repo.get_objects(raw_filters=raw_filters, user_id=user.id)
    except BaseRepoError:
        raise BaseApiError
    return bookings


# TODO: эту ручку может дергать только менеджер, сделать по аналогии с CurrentAdminUserDep
# TODO: но эту ручку может дергать и тот, кому принадлежит заказ...
@router.get("/{booking_id}")
async def get_booking(booking_id: int, booking_repo: BookingRepoDep) -> BookingSchema:
    try:
        booking = await booking_repo.get_object(id=booking_id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except MultipleResultsRepoError:
        raise MultipleResultsApiError
    except BaseRepoError:
        raise BaseApiError
    # TODO: to_api_model().with_wrapper() ??? (видел в другом проекте. понять: зачем это)
    return booking


@router.post("/")
async def create_booking(booking: BookingSchema):
    # TODO: Не дать создать заказ, если на выбранный период все комнаты данного типа будут заняты
    pass
