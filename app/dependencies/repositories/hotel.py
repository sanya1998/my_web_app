from typing import Annotated

from app.dependencies.db import PostgresSessionDep
from app.repositories import HotelRepo
from fastapi import Depends


def get_hotel_repo(session: PostgresSessionDep):
    return HotelRepo(session=session)


HotelRepoDep = Annotated[HotelRepo, Depends(get_hotel_repo)]
