from pydantic import BaseModel
from sqlalchemy_filterset import AsyncFilterSet


class _BaseFilterSet(AsyncFilterSet):
    # Здесь указывается типы фильтров ("=", ">", "<", "in" etc)
    pass


class BaseFilterSchema(BaseModel):
    # Здесь указывается типы переменных и значения по умолчанию
    pass
