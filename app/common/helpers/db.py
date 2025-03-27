from enum import Enum

from app.common.constants.order_by import PREFIX_DESC
from sqlalchemy import ColumnCollection, inspect


def get_columns_by_table(table) -> ColumnCollection:
    # TODO: точно ли нельзя просто table.column ?
    return inspect(table).c


def get_columns_names(table):
    return [column.name for column in table.__mapper__.columns]


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
