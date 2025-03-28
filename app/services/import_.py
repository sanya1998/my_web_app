from app.repositories.base import BaseRepository
from app.services.base import BaseService
from fastapi import UploadFile


class ImportService(BaseService):
    @BaseService.catcher
    def __init__(self, repo: BaseRepository):
        self.repo = repo

    @BaseService.catcher
    async def import_csv(self, file: UploadFile):
        # TODO: все, что касается бд засунуть в репозиторий

        # Запасной план:
        # csv_reader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
        # list(csv_reader) - список словарей
        # csv_reader.fieldnames - список заголовков

        raw_connection = (await (await self.repo.session.connection()).get_raw_connection()).driver_connection
        await raw_connection.copy_to_table(
            self.repo.db_model.__tablename__, source=file.file, format="csv", encoding="utf-8"
        )
        await self.repo.session.commit()
