from typing import Annotated

from app.common.dependencies.db.postgres import PostgresSessionDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.repositories.base import BaseRepoError
from app.repositories.hotel import HotelRepo
from fastapi import Depends


def get_hotel_repo(session: PostgresSessionDep):
    try:
        return HotelRepo(session=session)
    except BaseRepoError:
        raise BaseApiError


HotelRepoDep = Annotated[HotelRepo, Depends(get_hotel_repo)]
