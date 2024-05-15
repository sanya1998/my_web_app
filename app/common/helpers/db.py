from enum import Enum

from sqlalchemy import inspect


def get_columns_by_table(table):
    return inspect(table).c


def get_ordering_enum_by_columns(*args):
    key_value = dict()
    for column in args:
        name = column.name
        key_value[name.upper()] = name
        key_value[f"{name.upper()}_"] = f"-{name}"
    return Enum("OrderingEnum", key_value)
