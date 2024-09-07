from app.common.filtersets.rooms import RoomsFiltersSet
from app.common.schemas.room import RoomCreateSchema, RoomReadSchema
from app.common.tables import Rooms
from app.repositories.base import BaseRepository


class RoomRepo(BaseRepository):
    db_model = Rooms

    read_schema = RoomReadSchema
    create_schema = RoomCreateSchema

    filter_set = RoomsFiltersSet
