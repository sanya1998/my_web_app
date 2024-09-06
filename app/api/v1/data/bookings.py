from typing import List

from app.common.dependencies.auth.base import CurrentUserDep
from app.common.dependencies.auth.manager import CurrentManagerUserDep
from app.common.dependencies.filters.bookings import BookingsFiltersDep
from app.common.dependencies.input.bookings import BookingInputDep
from app.common.dependencies.repositories.booking import BookingRepoDep
from app.common.dependencies.services.booking import BookingServiceDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.multiple_results import MultipleResultsApiError
from app.common.exceptions.api.not_found import NotFoundApiError
from app.common.exceptions.api.unavailable import UnavailableApiError
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.multiple_results import MultipleResultsRepoError
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.exceptions.services.base import BaseServiceError
from app.common.exceptions.services.not_found import NotFoundServiceError
from app.common.exceptions.services.unavailable import UnavailableServiceError
from app.common.schemas.booking import BookingReadSchema
from fastapi import APIRouter

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/")
async def get_my_bookings(
    raw_filters: BookingsFiltersDep, booking_repo: BookingRepoDep, user: CurrentUserDep
) -> List[BookingReadSchema]:
    try:
        return await booking_repo.get_objects(raw_filters=raw_filters, user_id=user.id)
    except BaseRepoError:
        raise BaseApiError


@router.get("/{booking_id}")
async def get_my_booking(booking_id: int, booking_repo: BookingRepoDep, user: CurrentUserDep) -> BookingReadSchema:
    try:
        return await booking_repo.get_object(id=booking_id, user_id=user.id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except MultipleResultsRepoError:
        raise MultipleResultsApiError
    except BaseRepoError:
        raise BaseApiError


@router.get("/{booking_id}/for_manager")
async def get_booking_for_manager(
    booking_id: int, booking_repo: BookingRepoDep, manager: CurrentManagerUserDep
) -> BookingReadSchema:
    try:
        return await booking_repo.get_object(id=booking_id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except MultipleResultsRepoError:
        raise MultipleResultsApiError
    except BaseRepoError:
        raise BaseApiError


@router.post("/")
async def create_booking(
    booking_input: BookingInputDep, booking_service: BookingServiceDep, user: CurrentUserDep
) -> BookingReadSchema:
    try:
        return await booking_service.create_booking(booking_input, user_id=user.id)
    except NotFoundServiceError:
        raise NotFoundApiError
    except UnavailableServiceError:
        raise UnavailableApiError
    except BaseServiceError:
        raise BaseApiError
