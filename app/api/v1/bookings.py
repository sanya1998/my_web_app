from fastapi import APIRouter
from sqlalchemy import select

from app.common.dependencies.db.db import SessionDep
from app.common.models.bookings import SBooking
from app.common.tables import Bookings

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/")
async def get_bookings(session: SessionDep):
    query = select(Bookings)
    result = await session.execute(query)
    bookings = result.scalars().all()
    return bookings


@router.get("/{booking_id}")
async def get_booking(booking_id: int):
    # request.app.
    pass


@router.post("/")
async def add_booking(booking: SBooking):
    pass
