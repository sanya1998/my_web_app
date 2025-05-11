import codecs
import csv
import io

import pytest
from app.common.constants.api import ALL_PATH, FILTERED_PATH
from app.common.constants.info_types import InfoTypes
from app.common.tables import Bookings, Hotels, Rooms, Users
from app.common.tables.base import metadata
from app.config.common import settings
from app.resources.postgres import engine
from httpx import AsyncClient, QueryParams
from starlette import status
from tests.constants.urls import ROOT_V1_EXPORT, ROOT_V1_IMPORT

INFO_TYPE_MAP_TABLE = {
    InfoTypes.HOTELS: Hotels,
    InfoTypes.ROOMS: Rooms,
    InfoTypes.BOOKINGS: Bookings,
    InfoTypes.USERS: Users,
}


async def export_file(admin_client: AsyncClient, info_type: str, params: QueryParams = None):
    path = FILTERED_PATH if params else ALL_PATH
    info_type_path = f"/{info_type}"
    response_export = await admin_client.get(f"{ROOT_V1_EXPORT}{path}{info_type_path}", params=params)
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
    info_type = InfoTypes.BOOKINGS.value
    info_type_path = f"/{info_type}"
    file = await export_file(admin_client, info_type)

    if with_deleting:
        tables = [INFO_TYPE_MAP_TABLE.get(InfoTypes.BOOKINGS).__table__]
        async with engine.begin() as conn:
            await conn.run_sync(metadata.drop_all, tables=tables)
            await conn.run_sync(metadata.create_all, tables=tables)

    response_import = await admin_client.post(f"{ROOT_V1_IMPORT}{ALL_PATH}{info_type_path}", files={"file": file})
    assert response_import.status_code == status_code


async def test_filtered_export(admin_client: AsyncClient):
    exclude_id = 1
    info_type = InfoTypes.ROOMS.value
    file = await export_file(admin_client, info_type, QueryParams(id__not_in=[exclude_id]))
    csv_reader = csv.DictReader(codecs.iterdecode(file, settings.FILE_ENCODING))
    not_found_exclude = all(int(room["id"]) != exclude_id for room in csv_reader)
    assert not_found_exclude

    file = await export_file(admin_client, info_type)
    csv_reader = csv.DictReader(codecs.iterdecode(file, settings.FILE_ENCODING))
    found_include = any(int(room["id"]) == exclude_id for room in csv_reader)
    assert found_include
