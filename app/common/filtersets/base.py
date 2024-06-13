from sqlalchemy_filterset import LimitOffsetFilter
from sqlalchemy_filterset.filtersets import BaseFilterSet


class BaseCustomFilterSet(BaseFilterSet):
    # Здесь указываются типы фильтров ("=", ">", "<", "in" итд)
    pagination = LimitOffsetFilter()
