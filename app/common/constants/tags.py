from enum import Enum


class TagsEnum(str, Enum):
    SRV = "srv"
    USERS = "Users"
    HOTELS = "Hotels"
    ROOMS = "Rooms"
    BOOKINGS = "Bookings"
    MEDIA = "Media"
    FRONTEND = "Frontend"
    INTERNAL = "Internal"
