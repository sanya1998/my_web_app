from typing import Annotated

from app.dependencies.db import PostgresSessionDep
from app.repositories import BookingRepo
from fastapi import Depends


def get_booking_repo(session: PostgresSessionDep):
    return BookingRepo(session=session)


BookingRepoDep = Annotated[BookingRepo, Depends(get_booking_repo)]
