from typing import Annotated, Any, List

from app.config.main import settings
from fastapi import Depends, Query
from pydantic import BaseModel, ConfigDict, Field
from pydantic_filters import BaseFilter, PagePagination
from pydantic_filters.plugins.fastapi import FilterDepends, PaginationDepends


class CustomFilter(BaseFilter):
    model_config = ConfigDict(use_enum_values=True)


class CustomSort(BaseModel):
    """
    pydantic_filters.BaseSort может сортировать только по одному полю
    """

    ordering: List | None = Field(Query(None))

    model_config = ConfigDict(use_enum_values=True)


class CustomPagePagination(PagePagination):
    per_page: int = Field(settings.LIMIT_DEFAULT, ge=1, le=settings.LIMIT_MAX)


class Parameters(BaseModel):
    filters: Any
    sorts: Any
    pagination: Any


def create_depends(filters_class=CustomFilter, sorts_class=CustomSort, pagination_class=CustomPagePagination):
    def parameters(
        filters: Annotated[filters_class, FilterDepends(filters_class)],
        sorts: Annotated[sorts_class, Depends(sorts_class)],  # TODO: Depends не из pydantic-filters
        pagination: Annotated[pagination_class, PaginationDepends(pagination_class)],
    ):
        return Parameters(filters=filters, sorts=sorts, pagination=pagination)

    return Annotated[Parameters, Depends(parameters)]
