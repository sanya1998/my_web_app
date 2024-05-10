from fastapi import APIRouter
from sqlalchemy import select
from starlette.requests import Request

from app.common.dependencies.db.db import SessionDep
from app.common.models.bookings import SBooking
from app.common.tables import Bookings

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("/")
async def get_bookings(request: Request, session: SessionDep):
    # 1 вариант
    print(type(session), session)
    query = select(Bookings)
    result = await session.execute(query)
    bookings = result.scalars().all()
    print(bookings)

    print(type(request.app.state.db), request.app.state.db)
    # 2 вариант
    async with request.app.state.db() as session:
        print(type(session), session)
        query = select(Bookings)
        result = await session.execute(query)
        bookings = result.scalars().all()
        print(bookings)
        return bookings


@router.get("/{booking_id}")
async def get_booking(booking_id: int):
    # request.app.
    pass


@router.post("/")
async def add_booking(booking: SBooking):
    pass
