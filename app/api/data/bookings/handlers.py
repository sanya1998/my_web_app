from typing import Annotated, List, Union

from app.common.constants.roles import BookingsRecipientRoleEnum
from app.common.dependencies.auth import CurrentUserDep, ManagerOrUserDep, ManagerUserDep
from app.common.dependencies.filters import BookingsQueryParamsDep
from app.common.dependencies.input import BookingInputCreateDep, BookingInputUpdateDep
from app.common.dependencies.repositories import BookingRepoDep
from app.common.dependencies.services import BookingServiceDep
from app.common.exceptions.api import (
    BaseApiError,
    ForbiddenApiError,
    MultipleResultsApiError,
    NotFoundApiError,
    UnavailableApiError,
)
from app.common.exceptions.repositories import BaseRepoError, NotFoundRepoError
from app.common.exceptions.services import (
    BaseServiceError,
    ForbiddenServiceError,
    MultipleResultsServiceError,
    NotFoundServiceError,
    UnavailableServiceError,
)
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.schemas.booking import BookingBaseReadSchema, BookingReadSchema, CurrentUserBookingReadSchema
from app.common.tasks.email import send_booking_notify_email
from fastapi import Path

router = VersionedAPIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/")
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


@router.get("/", response_model_by_alias=False)
async def get_bookings_for_manager_or_current_user(
    query_params: BookingsQueryParamsDep,
    booking_service: BookingServiceDep,
    manager_or_user: ManagerOrUserDep,
) -> List[Union[BookingReadSchema, CurrentUserBookingReadSchema]]:
    """
    Получение бронирований с применением фильтров:
    - для менеджера: все бронирования
    - для обычного пользователя: только его бронирования
    """
    try:
        return await booking_service.get_list(client=manager_or_user, params=query_params)
    except BaseServiceError:
        raise BaseApiError


@router.get("/{object_id}", response_model_by_alias=False)
async def get_booking_for_manager_or_current_user(
    object_id: Annotated[int, Path(gt=0)],
    recipient_role: BookingsRecipientRoleEnum,
    booking_service: BookingServiceDep,
    manager_or_user: ManagerOrUserDep,
) -> Union[BookingReadSchema, CurrentUserBookingReadSchema]:
    """
    Получение бронирования с применением фильтров:
    - для менеджера: любое бронирование
    - для обычного пользователя: одно из его бронирований
    """
    try:
        return await booking_service.get_object(
            client=manager_or_user, recipient_role=recipient_role, object_id=object_id
        )
    except NotFoundServiceError:
        raise NotFoundApiError
    except MultipleResultsServiceError:
        raise MultipleResultsApiError
    except ForbiddenServiceError:
        raise ForbiddenApiError
    except BaseServiceError:
        raise BaseApiError


@router.put("/{object_id}")
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


@router.delete("/{object_id}")
async def delete_booking_for_manager(
    object_id: int, booking_repo: BookingRepoDep, manager: ManagerUserDep
) -> BookingBaseReadSchema:
    try:
        return await booking_repo.delete_object(id=object_id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except BaseRepoError:
        raise BaseApiError
