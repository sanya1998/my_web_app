from typing import List, Union

from app.common.constants.roles import BookingsRecipientRoleEnum
from app.common.helpers.check_data import CheckData
from app.common.schemas.booking import (
    BookingCreateSchema,
    BookingReadSchema,
    BookingUpdateSchema,
    CurrentUserBookingReadSchema,
)
from app.common.schemas.user import UserBaseReadSchema
from app.dependencies.filters import BookingsQueryParams
from app.dependencies.input import BookingCreateInputSchema, BookingUpdateInputSchema
from app.exceptions.repositories import NotFoundRepoError
from app.exceptions.services import (
    ForbiddenServiceError,
    NotFoundServiceError,
    UnavailableServiceError,
)
from app.repositories import BookingRepo, RoomRepo
from app.services.base import BaseService


class BookingService(BaseService):
    @BaseService.catcher
    def __init__(
        self,
        booking_repo: BookingRepo,
        room_repo: RoomRepo,
    ):
        self.booking_repo = booking_repo
        self.room_repo = room_repo
        self.check_data: CheckData | None = None
        self.selected_room_id: int | None = None

    @BaseService.catcher
    async def select_room_and_check_dates(self):
        selected_room = await self.room_repo.get_room_by_id_and_dates(
            check_data=self.check_data, room_id=self.selected_room_id
        )
        if selected_room is None:
            raise UnavailableServiceError
        return selected_room

    @BaseService.catcher
    async def create(self, booking_input: BookingCreateInputSchema, user_id: int):
        self.selected_room_id = booking_input.room_id
        self.check_data = CheckData(
            check_into=booking_input.date_from,
            check_out=booking_input.date_to,
        )
        selected_room = await self.select_room_and_check_dates()
        booking_create = BookingCreateSchema(user_id=user_id, price=selected_room.price, **booking_input.model_dump())
        return await self.booking_repo.create(booking_create)

    @BaseService.catcher
    async def update(self, booking_input: BookingUpdateInputSchema, booking_id: int):
        try:
            unchanged_booking = await self.booking_repo.get_object(id=booking_id)
            self.selected_room_id = unchanged_booking.room_id
        except NotFoundRepoError:
            raise NotFoundServiceError
        self.check_data = CheckData(
            check_into=booking_input.date_from,
            check_out=booking_input.date_to,
            exclude_booking_ids=[booking_id],
        )
        await self.select_room_and_check_dates()
        booking_update = BookingUpdateSchema.model_validate(booking_input)
        return await self.booking_repo.update(booking_update, id=booking_id)

    @BaseService.catcher
    async def get_list(
        self, client: UserBaseReadSchema, params: BookingsQueryParams
    ) -> List[Union[BookingReadSchema, CurrentUserBookingReadSchema]]:
        # TODO: remove recipient_role from params
        if params.recipient_role == BookingsRecipientRoleEnum.USER:
            return await self.booking_repo.get_objects_self(filters=params, user_id=client.id)

        return await self.booking_repo.get_objects(filters=params)

    @BaseService.catcher
    async def get_object(
        self, client: UserBaseReadSchema, recipient_role: BookingsRecipientRoleEnum, object_id: int
    ) -> Union[BookingReadSchema, CurrentUserBookingReadSchema]:
        method_map = {
            BookingsRecipientRoleEnum.USER: self.booking_repo.get_object_self,
            BookingsRecipientRoleEnum.MANAGER: self.booking_repo.get_object,
        }
        try:
            booking = await method_map[recipient_role](id=object_id)
        except NotFoundRepoError:
            raise NotFoundServiceError

        if recipient_role == BookingsRecipientRoleEnum.USER and booking.user_id != client.id:
            raise ForbiddenServiceError

        return booking
