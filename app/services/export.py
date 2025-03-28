import csv
import io

from app.common.dependencies.filters.export import ExportFilters
from app.common.helpers.db import get_columns_names
from app.repositories.base import BaseRepository
from app.services.base import BaseService
from fastapi.responses import StreamingResponse


class ExportService(BaseService):
    class Writer:
        @staticmethod
        def write(line):
            return line

    @BaseService.catcher
    def __init__(self, repo: BaseRepository):
        self.repo = repo

    @BaseService.catcher
    def iter_csv(self, data):
        writer = csv.writer(self.Writer())
        titles = get_columns_names(self.repo.db_model)
        yield writer.writerow(titles)
        for curr in data:
            yield writer.writerow([getattr(curr, title) for title in titles])

    @BaseService.catcher
    async def filtered_export_csv(self, filters: ExportFilters):
        data = await self.repo.get_raw_objects(filters)
        # TODO: мб response на более высоком уровне создавать?
        response = StreamingResponse(content=self.iter_csv(data), media_type="text/csv")
        filename = f"{self.repo.db_model.__tablename__}.csv"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    @BaseService.catcher
    async def export_csv(self):
        # TODO: в енвы вынести аргументы copy_from_table и copy_to_table
        # TODO: не нужно ли тут что-либо закрывать?
        raw_connection = (await (await self.repo.session.connection()).get_raw_connection()).driver_connection

        filename = f"{self.repo.db_model.__tablename__}.csv"
        stream = io.BytesIO()
        # TODO: использовать copy_from_query, чтобы учитывать фильтрацию (либо два варианта all и filtered)
        await raw_connection.copy_from_table(
            self.repo.db_model.__tablename__, output=stream, format="csv", encoding="utf-8"
        )
        stream.seek(0)
        # TODO: мб response на более высоком уровне создавать?
        response = StreamingResponse(content=stream, media_type="text/csv")
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    # TODO: больше не используется
    @BaseService.catcher
    async def create_csv_on_hard_disk(self, filters: ExportFilters, filename: str = "my_dump.csv"):
        data = await self.repo.get_raw_objects(filters)
        with open(filename, "w", newline="") as outfile:
            outcsv = csv.writer(outfile)
            titles = get_columns_names(self.repo.db_model)
            outcsv.writerow(titles)
            [outcsv.writerow([getattr(curr, title) for title in titles]) for curr in data]
