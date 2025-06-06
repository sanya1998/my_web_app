from typing import Annotated, List, Union

from app.common.constants.paths import BOOKINGS_PATH, PATTERN_OBJECT_ID
from app.common.constants.roles import BookingsRecipientRoleEnum
from app.common.constants.tags import TagsEnum
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.helpers.response import BaseResponse
from app.common.schemas.booking import BookingBaseReadSchema, BookingReadSchema, CurrentUserBookingReadSchema
from app.dependencies.auth.roles.manager import ManagerDep
from app.dependencies.auth.roles.manager_user import ManagerOrUserAnn
from app.dependencies.auth.token import CurrentUserAnn
from app.dependencies.filters import BookingsQueryParamsDep
from app.dependencies.input import BookingInputCreateAnn, BookingInputUpdateAnn
from app.dependencies.repositories import BookingRepoAnn
from app.dependencies.services import BookingServiceAnn
from app.exceptions.api import ForbiddenApiError, NotFoundApiError, UnavailableApiError
from app.exceptions.repositories import NotFoundRepoError
from app.exceptions.services import ForbiddenServiceError, NotFoundServiceError, UnavailableServiceError
from app.tasks.email import send_booking_notify_email
from fastapi import Path
from starlette import status

router = VersionedAPIRouter(prefix=BOOKINGS_PATH, tags=[TagsEnum.BOOKINGS])


@router.post("/", response_model=BaseResponse[BookingBaseReadSchema], status_code=status.HTTP_201_CREATED)
async def create_booking_for_current_user(
    booking_input: BookingInputCreateAnn, booking_service: BookingServiceAnn, user: CurrentUserAnn
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


@router.get(
    "/",
    response_model=BaseResponse[List[Union[BookingReadSchema, CurrentUserBookingReadSchema]]],
    response_model_by_alias=False,
    summary="Получение бронирований для менеджера или для обычного пользователя",
    description="""
    Получение бронирований с применением фильтров:
    \n- для менеджера: все бронирования
    \n- для обычного пользователя: только его бронирования
    """,
    response_description="Бронирования, удовлетворяющие заданным фильтрам",
)
async def get_bookings_for_manager_or_current_user(
    query_params: BookingsQueryParamsDep,
    booking_service: BookingServiceAnn,
    manager_or_user: ManagerOrUserAnn,
):
    bookings = await booking_service.get_list(client=manager_or_user, params=query_params)
    return BaseResponse(content=bookings)


@router.get(
    PATTERN_OBJECT_ID,
    response_model=BaseResponse[Union[BookingReadSchema, CurrentUserBookingReadSchema]],
    response_model_by_alias=False,
)
async def get_booking_for_manager_or_current_user(
    object_id: Annotated[int, Path(gt=0)],
    recipient_role: BookingsRecipientRoleEnum,
    booking_service: BookingServiceAnn,
    manager_or_user: ManagerOrUserAnn,
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
        raise NotFoundApiError(detail="Booking was not found")  # TODO: дублирование
    except ForbiddenServiceError:
        raise ForbiddenApiError


@router.put(PATTERN_OBJECT_ID, response_model=BaseResponse[BookingBaseReadSchema], dependencies=[ManagerDep])
async def update_booking_for_manager(
    object_id: int,
    booking_input: BookingInputUpdateAnn,
    booking_service: BookingServiceAnn,
):
    try:
        booking = await booking_service.update(booking_input, booking_id=object_id)
        return BaseResponse(content=booking)
    except NotFoundServiceError:
        raise NotFoundApiError(detail="Booking was not found")  # TODO: дублирование


@router.delete(PATTERN_OBJECT_ID, response_model=BaseResponse[BookingBaseReadSchema], dependencies=[ManagerDep])
async def delete_booking_for_manager(object_id: int, booking_repo: BookingRepoAnn):
    try:
        booking = await booking_repo.delete_object(id=object_id)
        return BaseResponse(content=booking)
    except NotFoundRepoError:
        raise NotFoundApiError(detail="Booking was not found")  # TODO: дублирование
