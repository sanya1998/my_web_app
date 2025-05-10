from typing import List

from app.common.dependencies.filters.base import MainFilters, SearchFilters, get_depends_by_filters_model
from app.common.dependencies.filters.common import HotelBaseFilters, RoomsBaseFilters
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Hotels

columns = get_columns_by_table(Hotels)
HotelsOrderingEnum = get_ordering_enum_by_columns("HotelsOrderingEnum", columns.id, columns.name, columns.location)


class HotelsFilters(MainFilters, SearchFilters, HotelBaseFilters):
    id__not_in: List[int] | None = None
    location__ilike: str | None = None
    stars__ge: int | None = None
    services__contains: List[str] | None = None
    order_by: List[HotelsOrderingEnum] | None = [HotelsOrderingEnum.ID]
    rooms: RoomsBaseFilters

    class Helper(SearchFilters.Helper):
        search_fields = [columns.name, columns.location]


HotelsFiltersDep = get_depends_by_filters_model(HotelsFilters)
