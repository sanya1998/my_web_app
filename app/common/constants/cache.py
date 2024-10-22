from enum import Enum


class CacheBaseEnum(str, Enum):
    @classmethod
    def contains(cls, item) -> bool:
        return item in cls._value2member_map_


class CacheListingEnum(CacheBaseEnum):
    HOTELS = "hotels"


class CacheObjectEnum(CacheBaseEnum):
    HOTEL = "hotel"
