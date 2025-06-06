from app.common.constants.roles import AllRolesEnum
from app.common.schemas.user import UserBaseReadSchema
from app.services.auth.base import BaseAuthService


class RolesAuthService(BaseAuthService):
    @BaseAuthService.catcher
    def authenticate_admin_by_user(self, user: UserBaseReadSchema) -> bool:
        return AllRolesEnum.ADMIN in user.roles

    @BaseAuthService.catcher
    def authenticate_admin_or_moderator_by_user(self, user: UserBaseReadSchema) -> bool:
        return bool({AllRolesEnum.ADMIN, AllRolesEnum.MODERATOR}.intersection(user.roles))

    @BaseAuthService.catcher
    def authenticate_manager_by_user(self, user: UserBaseReadSchema) -> bool:
        return AllRolesEnum.MANAGER in user.roles

    @BaseAuthService.catcher
    def authenticate_manager_or_user_by_user(self, user: UserBaseReadSchema) -> bool:
        return bool({AllRolesEnum.MANAGER, AllRolesEnum.USER}.intersection(user.roles))

    @BaseAuthService.catcher
    def authenticate_moderator_by_user(self, user: UserBaseReadSchema) -> bool:
        return AllRolesEnum.MODERATOR in user.roles
