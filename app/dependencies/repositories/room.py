from typing import Annotated

from app.dependencies.db import PostgresSessionDep
from app.repositories import RoomRepo
from fastapi import Depends


def get_room_repo(session: PostgresSessionDep):
    return RoomRepo(session=session)


RoomRepoDep = Annotated[RoomRepo, Depends(get_room_repo)]
