from typing import Annotated, List

from app.common.dependencies.filters.base import MainFilters, get_depends_by_filters_model
from app.common.helpers.db import get_columns_by_table
from app.common.tables import Rooms
from app.config.common import settings
from pydantic import Field

columns = get_columns_by_table(Rooms)


class ExportFilters(MainFilters):
    id__not_in: List[int] | None = None
    limit: Annotated[int, Field(ge=1, le=settings.LIMIT_RAW_DATA_MAX)] = settings.LIMIT_RAW_DATA_DEFAULT
    order_by: List[str] | None = ["id"]


ExportFiltersDep = get_depends_by_filters_model(ExportFilters)
