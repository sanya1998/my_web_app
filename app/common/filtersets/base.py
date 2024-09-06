from sqlalchemy_filterset import LimitOffsetFilter
from sqlalchemy_filterset.filtersets import BaseFilterSet


class BaseFiltersSet(BaseFilterSet):
    # Здесь указываются типы фильтров ("=", ">", "<", "in" итд)
    pagination = LimitOffsetFilter()
