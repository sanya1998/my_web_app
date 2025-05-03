from enum import Enum


class StrEnum(str, Enum):
    pass


def extend_str_enum(*enums, enum_name="EnumName"):
    """
    Реализация наследования и/или объединения Enum
    """
    return StrEnum(enum_name, {i.name: i.value for e in enums for i in e})


def extend_enum(*enums, enum_name="EnumName"):
    return Enum(enum_name, {i.name: i.value for e in enums for i in e})
