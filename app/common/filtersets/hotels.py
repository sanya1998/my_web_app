from app.common.filtersets.base import BaseFiltersSet
from app.common.filtersets.custom_filters.join_hotels_rooms import JoinHotelsRoomsFilter
from app.common.filtersets.custom_sets.dates import DatesFiltersSet
from app.common.filtersets.custom_sets.prices import PricesFiltersSet
from app.common.tables import Hotels
from sqlalchemy_filterset import SearchFilter


class HotelsFiltersSet(BaseFiltersSet, PricesFiltersSet, DatesFiltersSet):
    join_rooms = JoinHotelsRoomsFilter()
    location = SearchFilter(Hotels.location)
