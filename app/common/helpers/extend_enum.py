from enum import Enum


def extend_enum(*enums, enum_name="EnumName"):
    return Enum(enum_name, {i.name: i.value for e in enums for i in e})
