from app.common.filtersets.base import BaseFiltersSet
from app.common.tables import Rooms
from sqlalchemy.sql.operators import ge, le
from sqlalchemy_filterset import RangeFilter


class RoomsFiltersSet(BaseFiltersSet):
    price = RangeFilter(Rooms.price, left_lookup_expr=ge, right_lookup_expr=le)
