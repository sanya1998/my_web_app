from app.common.filtersets.base import BaseFiltersSet
from app.common.filtersets.custom_sets.dates import DatesFiltersSet
from app.common.filtersets.custom_sets.prices import PricesFiltersSet
from app.common.tables import Rooms
from sqlalchemy_filterset import Filter, NullsPosition, OrderingField, OrderingFilter


class RoomsFiltersSet(BaseFiltersSet, PricesFiltersSet, DatesFiltersSet):
    hotel_id = Filter(Rooms.hotel_id)
    ordering = OrderingFilter(price=OrderingField(Rooms.price, nulls=NullsPosition.last))
