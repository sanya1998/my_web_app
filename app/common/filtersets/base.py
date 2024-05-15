from sqlalchemy_filterset import AsyncFilterSet, LimitOffsetFilter


class BaseAsyncFilterSet(AsyncFilterSet):
    # Здесь указываются типы фильтров ("=", ">", "<", "in" итд)
    pagination = LimitOffsetFilter()
