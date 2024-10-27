from enum import Enum


# TODO: не используется, но, возможно, пригодится
class BaseEnum(str, Enum):
    @classmethod
    def contains(cls, item) -> bool:
        return item in cls._value2member_map_
