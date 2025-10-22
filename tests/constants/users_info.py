from app.common.constants.roles import AllRolesEnum

USER_EMAIL = "sharik@moloko.ru"
USER_PASSWORD = "easy_password"

MODERATOR_EMAIL = "mod@mod.ru"
MODERATOR_PASSWORD = "easy_password"

MANAGER_EMAIL = "kot@pes.ru"
MANAGER_PASSWORD = "easy_password"

ADMIN_EMAIL = "fedor@moloko.ru"
ADMIN_PASSWORD = "hard_password"


CREDENTIALS = {
    AllRolesEnum.ADMIN: (ADMIN_EMAIL, ADMIN_PASSWORD),
    AllRolesEnum.MANAGER: (MANAGER_EMAIL, MANAGER_PASSWORD),
    AllRolesEnum.MODERATOR: (MODERATOR_EMAIL, MODERATOR_PASSWORD),
    AllRolesEnum.USER: (USER_EMAIL, USER_PASSWORD),
}
