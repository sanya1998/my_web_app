from app.repositories import UserRepo
from app.services.auth import ApiAuthService, RolesAuthService
from app.services.base import BaseService
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request


class CmsAuthService(ApiAuthService, RolesAuthService):
    @BaseService.catcher
    def __init__(self, request: Request, session: AsyncSession):
        self.session = session
        super().__init__(user_repo=UserRepo(self.session), request=request)

    @BaseService.catcher
    async def authenticate_admin_or_moderator_by_token(self, token: str) -> bool:
        return self.authenticate_admin_or_moderator_by_user(user=await self.get_user(token=token))

    @BaseService.catcher
    async def authenticate_admin_or_moderator(self) -> bool:
        # TODO: нужна ли проверка токена на None?
        return await self.authenticate_admin_or_moderator_by_token(token=self.get_token())
