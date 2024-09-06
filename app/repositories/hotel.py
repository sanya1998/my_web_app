from app.common.filtersets.hotels import HotelsFiltersSet
from app.common.schemas.hotel import HotelCreateSchema, HotelReadSchema
from app.common.tables import Hotels
from app.repositories.base import BaseRepository


class HotelRepo(BaseRepository):
    db_model = Hotels

    read_schema = HotelReadSchema
    create_schema = HotelCreateSchema

    filter_set = HotelsFiltersSet
