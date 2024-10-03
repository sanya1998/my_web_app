from typing import List

from app.common.dependencies.filters_input.rooms import RoomsFiltersDep
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


@router.get("/{room_id}")
async def get_room(room_id: int, room_repo: RoomRepoDep) -> OneRoomReadSchema:
    try:
        return await room_repo.get_object(id=room_id)
    except NotFoundRepoError:
        raise NotFoundApiError
    except MultipleResultsRepoError:
        raise MultipleResultsApiError
    except BaseRepoError:
        raise BaseApiError


@router.get("/")
async def get_rooms(raw_filters: RoomsFiltersDep, room_repo: RoomRepoDep) -> List[ManyRoomsReadSchema]:
    """
    Возвращает все типы комнат.
    Поля remain_by_room, total_cost заполняются, только если есть date_to и date_from
    """
    try:
        return await room_repo.get_objects(raw_filters=raw_filters)
    except BaseRepoError:
        raise BaseApiError
