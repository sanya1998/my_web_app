from enum import Enum
from typing import Union

from app.common.helpers.extend_enum import extend_str_enum


class AdminRole(str, Enum):
    ADMIN = "admin"


class ManagerRole(str, Enum):
    MANAGER = "manager"


class ModeratorRole(str, Enum):
    MODERATOR = "moderator"


class UserRole(str, Enum):
    USER = "user"


# Для пользователя какой роли предназначен функционал
BookingsRecipientRoleEnum: Union[ManagerRole, UserRole] = extend_str_enum(
    ManagerRole, UserRole, enum_name="BookingsRecipientRoleEnum"
)

AllRolesEnum: Union[AdminRole, ManagerRole, ModeratorRole, UserRole] = extend_str_enum(
    AdminRole, ManagerRole, ModeratorRole, UserRole, enum_name="AllRolesEnum"
)
