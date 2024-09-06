from app.common.filtersets.base import BaseFiltersSet
from app.common.tables import Hotels
from sqlalchemy_filterset import SearchFilter


class HotelsFiltersSet(BaseFiltersSet):
    location: str = SearchFilter(Hotels.location)
