from enum import Enum


class RolesEnum(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    MODERATOR = "moderator"
