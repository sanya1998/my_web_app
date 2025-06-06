from app.repositories import UserRepo
from app.resources.postgres import async_session
from app.services import BaseService
from app.services.auth import ApiAuthService, RolesAuthService
from starlette.requests import Request


class CmsAuthService(ApiAuthService, RolesAuthService):
    @BaseService.catcher
    def __init__(self, request: Request):
        self.session = async_session()
        super().__init__(user_repo=UserRepo(self.session), request=request)

    @BaseService.catcher
    def __del__(self):
        self.session.close()

    @BaseService.catcher
    async def authenticate_admin_or_moderator_by_token(self, token: str) -> bool:
        return self.authenticate_admin_or_moderator_by_user(user=await self.get_user(token=token))

    @BaseService.catcher
    async def authenticate_admin_or_moderator(self) -> bool:
        # TODO: нужна ли проверка токена на None?
        return await self.authenticate_admin_or_moderator_by_token(token=self.get_token())
