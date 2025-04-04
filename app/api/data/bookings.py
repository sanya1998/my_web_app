from typing import List

from app.common.dependencies.auth.base import CurrentUserDep
from app.common.dependencies.auth.manager import ManagerUserDep
from app.common.dependencies.filters.bookings import BookingsFiltersDep, CurrentUserBookingsFiltersDep
from app.common.dependencies.input.bookings import BookingInputCreateDep, BookingInputUpdateDep
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
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.schemas.booking import BookingBaseReadSchema, BookingReadSchema, CurrentUserBookingReadSchema
from app.common.tasks.email import send_booking_notify_email

router = VersionedAPIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/for_current_user")
async def create_booking_for_current_user(
    booking_input: BookingInputCreateDep, booking_service: BookingServiceDep, user: CurrentUserDep
) -> BookingBaseReadSchema:
    try:
        booking = await booking_service.create(booking_input, user_id=user.id)
        booking_dict = booking.model_dump()
        send_booking_notify_email.delay(booking_dict, user.email)
        return booking
    except NotFoundServiceError:
        raise NotFoundApiError
    except UnavailableServiceError:
        raise UnavailableApiError
    except BaseServiceError:
        raise BaseApiError


@router.get("/for_current_user", response_model_by_alias=False)
async def get_bookings_for_current_user(
    filters: CurrentUserBookingsFiltersDep, booking_repo: BookingRepoDep, user: CurrentUserDep
) -> List[CurrentUserBookingReadSchema]:
    try:
        return await booking_repo.get_objects(filters=filters, user_id=user.id)
    except BaseRepoError:
        raise BaseApiError


@router.get("/for_manager", response_model_by_alias=False)
async def get_bookings_for_manager(
    filters: BookingsFiltersDep, booking_repo: BookingRepoDep, manager: ManagerUserDep
) -> List[BookingReadSchema]:
    try:
        return await booking_repo.get_objects(filters=filters)
    except BaseRepoError:
        raise BaseApiError


@router.get("/{object_id}/for_current_user", response_model_by_alias=False)
async def get_booking_for_current_user(
    object_id: int, booking_repo: BookingRepoDep, user: CurrentUserDep
) -> CurrentUserBookingReadSchema:
    """Если запрашиваемое бронирование существует, но не принадлежит пользователю, то ответ NotFoundApiError"""
    try:
        return await booking_repo.get_object(id=object_id, user_id=user.id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except MultipleResultsRepoError:
        raise MultipleResultsApiError
    except BaseRepoError:
        raise BaseApiError


@router.get("/{object_id}/for_manager", response_model_by_alias=False)
async def get_booking_for_manager(
    object_id: int, booking_repo: BookingRepoDep, manager: ManagerUserDep
) -> BookingReadSchema:
    try:
        return await booking_repo.get_object(id=object_id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except MultipleResultsRepoError:
        raise MultipleResultsApiError
    except BaseRepoError:
        raise BaseApiError


@router.put("/{object_id}/for_manager")
async def update_booking_for_manager(
    object_id: int,
    booking_input: BookingInputUpdateDep,
    booking_service: BookingServiceDep,
    manager: ManagerUserDep,
) -> BookingBaseReadSchema:
    try:
        return await booking_service.update(booking_input, booking_id=object_id)
    except NotFoundServiceError:
        raise NotFoundApiError
    except BaseServiceError:
        raise BaseApiError


@router.delete("/{object_id}/for_manager")
async def delete_booking_for_manager(
    object_id: int, booking_repo: BookingRepoDep, manager: ManagerUserDep
) -> BookingBaseReadSchema:
    try:
        return await booking_repo.delete_object(id=object_id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except BaseRepoError:
        raise BaseApiError
