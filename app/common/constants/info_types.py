from enum import Enum
from typing import Union

from app.common.helpers.extend_enum import extend_str_enum


class DataTypes(str, Enum):
    HOTELS: str = "hotels"
    ROOMS: str = "rooms"
    BOOKINGS: str = "bookings"


class OtherTypes(str, Enum):
    USERS: str = "users"


InfoTypes: Union[DataTypes, OtherTypes] = extend_str_enum(DataTypes, OtherTypes, enum_name="InfoTypes")
