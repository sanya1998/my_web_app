from typing import List

from app.common.dependencies.filters.base import BaseFilterSchema, _BaseFilterSet
from app.common.exceptions.repositories.base import BaseNotFoundError
from app.common.schemas.base import BaseSchema
from app.common.tables.base import BaseTable
from pydantic import parse_obj_as
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    db_model = BaseTable
    schema_model = BaseSchema
    exception_not_found = BaseNotFoundError
    filter_set = _BaseFilterSet
    filter_schema = BaseFilterSchema

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_objects(self, raw_filters: BaseFilterSchema) -> List[BaseSchema]:
        filter_set = self.filter_set(self.session, select(self.db_model))
        filter_params = raw_filters.model_dump(exclude_none=True)
        filtered_objects = await filter_set.filter(filter_params)
        print(filter_set.filter_query(filter_params))  # TODO: tmp
        # TODO: `return filtered_objects` тоже будет работать для FastApi (разобраться после того, как респонс будет)
        return parse_obj_as(list[self.schema_model], filtered_objects)

    async def get_object(self, object_id):
        query = select(self.db_model).where(self.db_model.id == object_id)
        result = await self.session.execute(query)
        try:
            obj = result.scalar_one()  # TODO: can use scalar_one_or_none()
        except NoResultFound:
            raise self.exception_not_found
        # TODO: что будет, если оставить только obj, после того, как респонс будет)
        return self.schema_model.from_orm(obj)

    async def create(self, data):
        raise NotImplementedError

    async def upsert(self, data):
        raise NotImplementedError

    async def update_object(self, object_id, data):
        raise NotImplementedError

    async def update_object_field(self, object_id, data):
        raise NotImplementedError

    async def delete(self, object_id):
        raise NotImplementedError
