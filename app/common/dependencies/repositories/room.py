from typing import Annotated

from app.common.dependencies.db import PostgresSessionDep
from app.common.exceptions.api import BaseApiError
from app.common.exceptions.repositories import BaseRepoError
from app.repositories import RoomRepo
from fastapi import Depends


def get_room_repo(session: PostgresSessionDep):
    try:
        return RoomRepo(session=session)
    except BaseRepoError:
        raise BaseApiError


RoomRepoDep = Annotated[RoomRepo, Depends(get_room_repo)]
