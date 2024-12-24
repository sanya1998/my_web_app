from enum import Enum
from typing import Type

from app.common.constants.order_by import PREFIX_DESC
from app.common.dependencies.parameters.base import CustomSort
from app.common.tables.base import BaseTable
from sqlalchemy import ColumnCollection, Select, desc, inspect


def get_columns_by_table(table) -> ColumnCollection:
    # TODO: точно ли нельзя просто table.column ?
    return inspect(table).c


def get_ordering_enum_by_columns(enum_name="OrderingEnum", *args):
    key_value = dict()
    for column in args:
        name = column.name
        name_upper = name.upper()
        key_value[name_upper] = name
        key_value[f"{name_upper}_"] = f"{PREFIX_DESC}{name}"
    return Enum(enum_name, key_value)


def get_back_populates(field) -> str:
    # TODO: если есть возможность, то надо красивее получить
    return str(field).split(".")[-1]


def append_sorts_to_statement(statement: Select, model: Type[BaseTable], sorts: CustomSort) -> Select:
    if sorts.ordering is None:
        return statement
    sort_fields = [
        desc(getattr(model, f[len(PREFIX_DESC) :])) if f.startswith(PREFIX_DESC) else getattr(model, f)
        for f in sorts.ordering
    ]
    return statement.order_by(*sort_fields)
