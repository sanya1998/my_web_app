from app.common.exceptions.repositories.already_exists import AlreadyExistsRepoError
from app.common.exceptions.services.already_exists import AlreadyExistsServiceError
from app.repositories.base import BaseRepository
from app.services.base import BaseService
from fastapi import UploadFile


class ImportService(BaseService):
    @BaseService.catcher
    def __init__(self, repo: BaseRepository):
        self.repo = repo

    @BaseService.catcher
    async def import_(self, file: UploadFile):
        try:
            await self.repo.import_(file)
        except AlreadyExistsRepoError:
            raise AlreadyExistsServiceError
