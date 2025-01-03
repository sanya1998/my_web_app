from datetime import date

import pytest
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.schemas.booking import BookingCreateSchema, BookingUpdateSchema
from app.repositories.booking import BookingRepo
from sqlalchemy.ext.asyncio import AsyncSession


async def test_bookings_total_cost(session: AsyncSession):
    booking_repo = BookingRepo(session)

    create_schema = BookingCreateSchema(
        date_from=date(2023, 7, 20),
        date_to=date(2023, 7, 25),
        price=3000,
        room_id=6,
        user_id=3,
    )

    created_booking = await booking_repo.create(data=create_schema)

    got_booking = await booking_repo.get_object(id=created_booking.id)
    assert got_booking.total_cost == create_schema.price * (create_schema.date_to - create_schema.date_from).days

    update_schema = BookingUpdateSchema.model_validate(create_schema)
    update_schema.price = create_schema.price + 5000
    updated_booking = await booking_repo.update(id=created_booking.id, data=update_schema)
    assert updated_booking.total_cost == update_schema.price * (update_schema.date_to - update_schema.date_from).days


async def test_repo_crud_bookings(session):
    booking_repo = BookingRepo(session)

    create_schema = BookingCreateSchema(
        date_from=date(2023, 7, 20),
        date_to=date(2023, 7, 25),
        price=3000,
        room_id=7,
        user_id=2,
    )
    created_booking = await booking_repo.create(data=create_schema)
    got_booking = await booking_repo.get_object(id=created_booking.id)
    await booking_repo.delete_object(id=got_booking.id)
    with pytest.raises(NotFoundRepoError):
        await booking_repo.get_object(id=created_booking.id)
