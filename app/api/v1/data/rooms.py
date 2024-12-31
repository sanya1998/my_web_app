from typing import List

from app.common.dependencies.filters.rooms import RoomsFiltersDep
from app.common.dependencies.repositories.room import RoomRepoDep
from app.common.exceptions.api.base import BaseApiError
from app.common.exceptions.api.multiple_results import MultipleResultsApiError
from app.common.exceptions.api.not_found import NotFoundApiError
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.multiple_results import MultipleResultsRepoError
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.schemas.room import ManyRoomsReadSchema, OneRoomReadSchema
from fastapi import APIRouter

router = APIRouter(prefix="/rooms", tags=["Rooms"])


@router.get("/{object_id}")
async def get_room(object_id: int, room_repo: RoomRepoDep) -> OneRoomReadSchema:
    try:
        return await room_repo.get_object(id=object_id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except MultipleResultsRepoError:
        raise MultipleResultsApiError
    except BaseRepoError:
        raise BaseApiError


@router.get("/")
async def get_rooms(filters: RoomsFiltersDep, room_repo: RoomRepoDep) -> List[ManyRoomsReadSchema]:
    """
    Возвращает все типы комнат.
    Если нет check_into и check_out, то remain_by_room == quantity, total_cost == 0.
    """
    try:
        return await room_repo.get_objects(filters=filters)
    except BaseRepoError:
        raise BaseApiError
