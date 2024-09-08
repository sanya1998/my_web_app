from app.common.tables import Rooms
from sqlalchemy.sql.operators import ge, le
from sqlalchemy_filterset import BaseFilterSet, RangeFilter


class PricesFiltersSet(BaseFilterSet):
    prices = RangeFilter(Rooms.price, left_lookup_expr=ge, right_lookup_expr=le)
