from typing import Annotated

from app.common.dependencies.db.postgres import PostgresSessionDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.repositories.base import BaseRepoError
from app.repositories.booking import BookingRepo
from fastapi import Depends


def get_booking_repo(session: PostgresSessionDep):
    try:
        return BookingRepo(session=session)
    except BaseRepoError:
        raise BaseApiError


BookingRepoDep = Annotated[BookingRepo, Depends(get_booking_repo)]
