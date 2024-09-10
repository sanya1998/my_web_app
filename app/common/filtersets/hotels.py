from app.common.filtersets.base import BaseFiltersSet
from app.common.filtersets.custom_sets.dates import DatesFiltersSet
from app.common.filtersets.custom_sets.prices import PricesFiltersSet
from app.common.tables import Hotels
from sqlalchemy_filterset import SearchFilter


class HotelsFiltersSet(BaseFiltersSet, PricesFiltersSet, DatesFiltersSet):
    location = SearchFilter(Hotels.location)
