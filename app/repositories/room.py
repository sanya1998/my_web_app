from app.common.filtersets.rooms import RoomsFiltersSet
from app.common.schemas.room import (
    ManyRoomsReadSchema,
    OneRoomReadSchema,
    RoomCreateSchema,
)
from app.common.tables import Rooms
from app.repositories.base import BaseRepository


class RoomRepo(BaseRepository):
    db_model = Rooms

    one_read_schema = OneRoomReadSchema
    many_read_schema = ManyRoomsReadSchema
    create_schema = RoomCreateSchema

    filter_set = RoomsFiltersSet
