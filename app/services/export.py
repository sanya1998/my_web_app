from app.common.dependencies.filters.export import ExportFilters
from app.repositories.base import BaseRepository
from app.services.base import BaseService


class ExportService(BaseService):
    @BaseService.catcher
    def __init__(self, repo: BaseRepository):
        self.repo = repo

    @BaseService.catcher
    async def export_all_in_csv(self):
        stream = await self.repo.export_all()
        return stream

    @BaseService.catcher
    async def export_filtered_in_csv(self, filters: ExportFilters):
        stream = await self.repo.export_filtered(filters)
        return stream
