from typing import Annotated

from app.common.dependencies.db.db import SessionDep
from app.repositories.booking import BookingRepo
from fastapi import Depends


def get_booking_repo(session: SessionDep):
    return BookingRepo(session=session)


BookingRepoDep = Annotated[BookingRepo, Depends(get_booking_repo)]
