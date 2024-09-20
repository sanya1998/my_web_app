from app.common.exceptions.services.not_found import NotFoundServiceError
from app.common.exceptions.services.unavailable import UnavailableServiceError
from app.common.schemas.booking import (
    BookingCreateInputSchema,
    BookingCreateSchema,
    BookingUpdateInputSchema,
    BookingUpdateSchema,
    CheckData,
)
from app.repositories.booking import BookingRepo
from app.services.base import BaseService


class BookingService(BaseService):
    @BaseService.catcher
    def __init__(
        self,
        booking_repo: BookingRepo,
    ):
        super().__init__()
        self.booking_repo = booking_repo
        self.check_data: CheckData | None = None

    @BaseService.catcher
    async def select_room_and_check_dates(self):
        selected_room = await self.booking_repo.get_room_info_by_id_and_dates(data=self.check_data)
        if selected_room is None:
            raise NotFoundServiceError
        if selected_room.remain < 1:
            raise UnavailableServiceError
        return selected_room

    @BaseService.catcher
    async def create(self, booking_input: BookingCreateInputSchema, user_id: int):
        self.check_data = CheckData(
            selected_room_id=booking_input.room_id,
            check_into=booking_input.date_from,
            check_out=booking_input.date_to,
        )
        selected_room = await self.select_room_and_check_dates()
        booking_create = BookingCreateSchema(user_id=user_id, price=selected_room.price, **booking_input.model_dump())
        return await self.booking_repo.create(booking_create)

    @BaseService.catcher
    async def update(self, booking_input: BookingUpdateInputSchema):
        unchanged_booking = await self.booking_repo.get_object(id=booking_input.id)
        self.check_data = CheckData(
            selected_room_id=unchanged_booking.room_id,
            check_into=booking_input.date_from,
            check_out=booking_input.date_to,
            exclude_booking_ids=[booking_input.id],
        )
        await self.select_room_and_check_dates()
        booking_update = BookingUpdateSchema.model_validate(booking_input)
        return await self.booking_repo.update(booking_update, id=booking_input.id)
