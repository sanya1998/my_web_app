from typing import Annotated

from app.dependencies.db import PostgresSessionAnn
from app.repositories import BookingRepo
from fastapi import Depends


def get_booking_repo(session: PostgresSessionAnn):
    return BookingRepo(session=session)


BookingRepoAnn = Annotated[BookingRepo, Depends(get_booking_repo)]
