from sqlalchemy_filterset import AsyncFilterSet


class _BaseFilterSet(AsyncFilterSet):
    # Здесь указываются типы фильтров ("=", ">", "<", "in" итд)
    pass
