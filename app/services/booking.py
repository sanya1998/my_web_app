from app.common.exceptions.services.not_found import NotFoundServiceError
from app.common.exceptions.services.unavailable import UnavailableServiceError
from app.common.schemas.booking import BookingCreateSchema, BookingInputSchema
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

    @BaseService.catcher
    async def create_booking(self, booking_input: BookingInputSchema, user_id: int):
        selected_room = await self.booking_repo.get_room_info(booking_input)
        if selected_room is None:
            raise NotFoundServiceError
        if selected_room.remain < 1:
            raise UnavailableServiceError
        booking_create = BookingCreateSchema(user_id=user_id, price=selected_room.prices, **booking_input.model_dump())
        return await self.booking_repo.create(booking_create)
