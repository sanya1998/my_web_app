from typing import Annotated

from app.dependencies.db import PostgresSessionAnn
from app.repositories import HotelRepo
from fastapi import Depends


def get_hotel_repo(session: PostgresSessionAnn):
    return HotelRepo(session=session)


HotelRepoAnn = Annotated[HotelRepo, Depends(get_hotel_repo)]
