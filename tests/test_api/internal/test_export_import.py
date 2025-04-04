import codecs
import csv
import io

import pytest
from app.common.constants.info_types import InfoTypes
from app.common.tables import Bookings, Hotels, Rooms, Users
from app.common.tables.base import metadata
from app.config.common import settings
from app.resources.postgres import engine
from httpx import AsyncClient, QueryParams
from starlette import status
from tests.constants import BASE_EXPORT_URL, BASE_IMPORT_URL

INFO_TYPE_MAP_TABLE = {
    InfoTypes.HOTELS: Hotels,
    InfoTypes.ROOMS: Rooms,
    InfoTypes.BOOKINGS: Bookings,
    InfoTypes.USERS: Users,
}


async def export_file(admin_client: AsyncClient, info_type_url: str, params: QueryParams = None):
    path = "filtered/" if params else "all/"
    response_export = await admin_client.get(f"{BASE_EXPORT_URL}{path}{info_type_url}for_admin", params=params)
    assert response_export.status_code == status.HTTP_200_OK
    file = io.BytesIO()
    file.write(response_export.content)

    #  TODO: сделать что-то вроде:
    # yield file
    # file.seek(0)

    file.seek(0)
    return file


@pytest.mark.parametrize(
    "with_deleting, status_code",
    [
        (False, status.HTTP_409_CONFLICT),
        (True, status.HTTP_200_OK),
    ],
)
async def test_all_export_all_import(admin_client: AsyncClient, with_deleting, status_code):
    info_type = InfoTypes.BOOKINGS
    info_type_url = f"{info_type.value}/"
    file = await export_file(admin_client, info_type_url)

    if with_deleting:
        tables = [INFO_TYPE_MAP_TABLE.get(info_type).__table__]
        async with engine.begin() as conn:
            await conn.run_sync(metadata.drop_all, tables=tables)
            await conn.run_sync(metadata.create_all, tables=tables)

    response_import = await admin_client.post(f"{BASE_IMPORT_URL}all/{info_type_url}for_admin", files={"file": file})
    assert response_import.status_code == status_code


async def test_filtered_export(admin_client: AsyncClient):
    exclude_id = 1

    info_type = InfoTypes.ROOMS
    info_type_url = f"{info_type.value}/"

    file = await export_file(admin_client, info_type_url, QueryParams(id__not_in=[exclude_id]))
    csv_reader = csv.DictReader(codecs.iterdecode(file, settings.FILE_ENCODING))
    not_found_exclude = all(int(room["id"]) != exclude_id for room in csv_reader)
    assert not_found_exclude

    file = await export_file(admin_client, info_type_url)
    csv_reader = csv.DictReader(codecs.iterdecode(file, settings.FILE_ENCODING))
    found_include = any(int(room["id"]) == exclude_id for room in csv_reader)
    assert found_include
