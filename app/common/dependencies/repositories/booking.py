from typing import Annotated

from app.common.dependencies.db import PostgresSessionDep
from app.common.exceptions.api import BaseApiError
from app.common.exceptions.repositories import BaseRepoError
from app.repositories import BookingRepo
from fastapi import Depends


def get_booking_repo(session: PostgresSessionDep):
    try:
        return BookingRepo(session=session)
    except BaseRepoError:
        raise BaseApiError


BookingRepoDep = Annotated[BookingRepo, Depends(get_booking_repo)]
