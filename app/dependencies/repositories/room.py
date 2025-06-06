from typing import Annotated

from app.dependencies.db import PostgresSessionAnn
from app.repositories import RoomRepo
from fastapi import Depends


def get_room_repo(session: PostgresSessionAnn):
    return RoomRepo(session=session)


RoomRepoAnn = Annotated[RoomRepo, Depends(get_room_repo)]
