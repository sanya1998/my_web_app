from typing import Annotated

from fastapi import Depends

from app.common.dependencies.db.db import SessionDep
from app.repositories.booking import BookingRepo


def get_booking_repo(session: SessionDep):
    return BookingRepo(session=session)


BookingRepoDep = Annotated[BookingRepo, Depends(get_booking_repo)]
