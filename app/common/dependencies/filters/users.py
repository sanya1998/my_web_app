from typing import List

from app.common.dependencies.filters.base import MainFilters, get_depends_by_filters_model
from app.common.dependencies.filters.common import UserBaseFilters
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Users

columns = get_columns_by_table(Users)
UsersOrderingEnum = get_ordering_enum_by_columns("UsersOrderingEnum", columns.id, columns.email)


class UsersFilters(MainFilters, UserBaseFilters):
    order_by: List[UsersOrderingEnum] | None = None


UsersFiltersDep = get_depends_by_filters_model(UsersFilters)
