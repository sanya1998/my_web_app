from typing import Annotated, List

from app.common.dependencies.filters.base import MainFilters, filter_depends
from app.common.helpers.db import get_columns_by_table
from app.common.tables import Rooms
from app.config.common import settings
from fastapi import Query
from pydantic import Field

columns = get_columns_by_table(Rooms)


class ExportFilters(MainFilters):
    limit: int = Field(settings.LIMIT_RAW_DATA_DEFAULT, ge=1, le=settings.LIMIT_RAW_DATA_MAX)
    order_by: List[str] | None = Field(Query(["id"]))


ExportFiltersDep = Annotated[ExportFilters, filter_depends(ExportFilters)]
