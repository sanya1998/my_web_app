from typing import Annotated, List

from app.common.constants.paths import PATTERN_OBJECT_ID, ROOMS_PATH
from app.common.constants.tags import TagsEnum
from app.common.helpers.api_version import VersionedAPIRouter
from app.common.helpers.response import BaseResponse
from app.common.schemas.room import ManyRoomsReadSchema, RoomReadSchema
from app.dependencies.filters import RoomsFiltersDep
from app.dependencies.repositories import RoomRepoDep
from app.exceptions.api import NotFoundApiError
from app.exceptions.repositories import NotFoundRepoError
from fastapi import Path

router = VersionedAPIRouter(prefix=ROOMS_PATH, tags=[TagsEnum.ROOMS])


@router.get("/", response_model=BaseResponse[List[ManyRoomsReadSchema]])
async def get_rooms(filters: RoomsFiltersDep, room_repo: RoomRepoDep):
    """
    Возвращает все типы комнат.
    Если нет check_into и check_out, то remain_by_room == quantity, total_cost == 0.
    """
    rooms = await room_repo.get_objects(filters=filters)
    return BaseResponse(content=rooms)


@router.get(PATTERN_OBJECT_ID, response_model=BaseResponse[RoomReadSchema], response_model_by_alias=False)
async def get_room(object_id: Annotated[int, Path(gt=0)], room_repo: RoomRepoDep):
    try:
        room = await room_repo.get_object(id=object_id)
        return BaseResponse(content=room)
    except NotFoundRepoError:
        raise NotFoundApiError(detail="Room was not found")
