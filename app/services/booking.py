from app.common.dependencies.input.bookings import BookingCreateInputSchema, BookingUpdateInputSchema
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.exceptions.services.not_found import NotFoundServiceError
from app.common.exceptions.services.unavailable import UnavailableServiceError
from app.common.helpers.check_data import CheckData
from app.common.schemas.booking import BookingCreateSchema, BookingUpdateSchema
from app.repositories.booking import BookingRepo
from app.repositories.room import RoomRepo
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
        self.check_data: CheckData
        self.selected_room_id: int

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
