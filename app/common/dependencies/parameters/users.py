from typing import List

from app.common.dependencies.parameters.base import CustomSort, create_depends
from app.common.helpers.db import get_columns_by_table, get_ordering_enum_by_columns
from app.common.tables import Users
from fastapi import Query
from pydantic import Field

columns = get_columns_by_table(Users)
UsersOrderingEnum = get_ordering_enum_by_columns("UsersOrderingEnum", columns.id, columns.email)


class UsersSorts(CustomSort):
    ordering: List[UsersOrderingEnum] | None = Field(Query(None))


UsersParametersDep = create_depends(sorts_class=UsersSorts)
