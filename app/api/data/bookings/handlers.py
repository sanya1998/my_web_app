from typing import Annotated, List, Union

from app.common.constants.paths import BOOKINGS_PATH, PATTERN_OBJECT_ID
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
from app.common.helpers.response import BaseResponse
from app.common.schemas.booking import BookingBaseReadSchema, BookingReadSchema, CurrentUserBookingReadSchema
from app.common.tasks.email import send_booking_notify_email
from fastapi import Path
from starlette import status

router = VersionedAPIRouter(prefix=BOOKINGS_PATH, tags=["Bookings"])


@router.post("/", response_model=BaseResponse[BookingBaseReadSchema], status_code=status.HTTP_201_CREATED)
async def create_booking_for_current_user(
    booking_input: BookingInputCreateDep, booking_service: BookingServiceDep, user: CurrentUserDep
):
    try:
        booking = await booking_service.create(booking_input, user_id=user.id)
        booking_dict = booking.model_dump()
        send_booking_notify_email.delay(booking_dict, user.email)
        return BaseResponse(content=booking)
    except NotFoundServiceError:
        raise NotFoundApiError
    except UnavailableServiceError:
        raise UnavailableApiError
    except BaseServiceError:
        raise BaseApiError


@router.get(
    "/",
    response_model=BaseResponse[List[Union[BookingReadSchema, CurrentUserBookingReadSchema]]],
    response_model_by_alias=False,
)
async def get_bookings_for_manager_or_current_user(
    query_params: BookingsQueryParamsDep,
    booking_service: BookingServiceDep,
    manager_or_user: ManagerOrUserDep,
):
    """
    Получение бронирований с применением фильтров:
    - для менеджера: все бронирования
    - для обычного пользователя: только его бронирования
    """
    try:
        bookings = await booking_service.get_list(client=manager_or_user, params=query_params)
        return BaseResponse(content=bookings)
    except BaseServiceError:
        raise BaseApiError


@router.get(
    PATTERN_OBJECT_ID,
    response_model=BaseResponse[Union[BookingReadSchema, CurrentUserBookingReadSchema]],
    response_model_by_alias=False,
)
async def get_booking_for_manager_or_current_user(
    object_id: Annotated[int, Path(gt=0)],
    recipient_role: BookingsRecipientRoleEnum,
    booking_service: BookingServiceDep,
    manager_or_user: ManagerOrUserDep,
):
    """
    Получение бронирования с применением фильтров:
    - для менеджера: любое бронирование
    - для обычного пользователя: одно из его бронирований
    """
    try:
        booking = await booking_service.get_object(
            client=manager_or_user, recipient_role=recipient_role, object_id=object_id
        )
        return BaseResponse(content=booking)
    except NotFoundServiceError:
        raise NotFoundApiError
    except MultipleResultsServiceError:
        raise MultipleResultsApiError
    except ForbiddenServiceError:
        raise ForbiddenApiError
    except BaseServiceError:
        raise BaseApiError


@router.put(PATTERN_OBJECT_ID, response_model=BaseResponse[BookingBaseReadSchema])
async def update_booking_for_manager(
    object_id: int,
    booking_input: BookingInputUpdateDep,
    booking_service: BookingServiceDep,
    manager: ManagerUserDep,
):
    try:
        booking = await booking_service.update(booking_input, booking_id=object_id)
        return BaseResponse(content=booking)
    except NotFoundServiceError:
        raise NotFoundApiError
    except BaseServiceError:
        raise BaseApiError


@router.delete(PATTERN_OBJECT_ID, response_model=BaseResponse[BookingBaseReadSchema])
async def delete_booking_for_manager(object_id: int, booking_repo: BookingRepoDep, manager: ManagerUserDep):
    try:
        booking = await booking_repo.delete_object(id=object_id)
        return BaseResponse(content=booking)
    except NotFoundRepoError:
        raise NotFoundApiError
    except BaseRepoError:
        raise BaseApiError
