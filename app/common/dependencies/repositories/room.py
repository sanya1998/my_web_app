from typing import Annotated

from app.common.dependencies.db.db import SessionDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.repositories.base import BaseRepoError
from app.repositories.room import RoomRepo
from fastapi import Depends


def get_room_repo(session: SessionDep):
    try:
        return RoomRepo(session=session)
    except BaseRepoError:
        raise BaseApiError


RoomRepoDep = Annotated[RoomRepo, Depends(get_room_repo)]