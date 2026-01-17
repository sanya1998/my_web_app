from enum import Enum


class TagsEnum(str, Enum):
    SRV = "srv"
    AUTH = "Auth"
    USERS = "Users"
    HOTELS = "Hotels"
    ROOMS = "Rooms"
    BOOKINGS = "Bookings"
    PRODUCTS = "Products"
    MEDIA = "Media"
    FRONTEND = "Frontend"
    INTERNAL = "Internal"
