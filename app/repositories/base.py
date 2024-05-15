from typing import List

from app.common.dependencies.api_args.base import BaseFilterSchema
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.not_found import RepoNotFoundError
from app.common.exceptions.repositories.type_error import RepoTypeError
from app.common.filtersets.base import BaseAsyncFilterSet
from app.common.schemas.base import BaseSchema
from app.common.tables.base import BaseTable
from pydantic import parse_obj_as
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    db_model = BaseTable
    schema_model = BaseSchema
    model_name = schema_model.__name__

    filter_set = BaseAsyncFilterSet
    filter_schema = BaseFilterSchema

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def catch_exception(method):
        async def wrapper(self, *args, **kwargs):
            try:
                return await method(self, *args, **kwargs)
            except TypeError:
                raise RepoTypeError(self.model_name, kwargs)
            except NoResultFound:
                raise RepoNotFoundError(self.model_name, kwargs)
            except Exception:
                raise BaseRepoError(self.model_name, kwargs)  # TODO: какие данные стоит передавать в исключение

        return wrapper

    @catch_exception
    async def get_objects(self, raw_filters: BaseFilterSchema) -> List[BaseSchema]:
        filter_set = self.filter_set(self.session, select(self.db_model))
        filter_params = raw_filters.model_dump(exclude_none=True)
        filtered_objects = await filter_set.filter(filter_params)
        # TODO: `return filtered_objects` тоже будет работать для FastApi (разобраться после того, как респонс будет)
        return parse_obj_as(list[self.schema_model], filtered_objects)

    @catch_exception
    async def get_object(self, object_id):
        query = select(self.db_model).where(self.db_model.id == object_id)
        result = await self.session.execute(query)
        obj = result.scalar_one()  # TODO: can use scalar_one_or_none() и подумать нужен ли self.exception_not_found
        # TODO: что будет, если оставить только obj, после того, как респонс будет)
        return self.schema_model.from_orm(obj)

    @catch_exception
    async def create(self, data):
        raise NotImplementedError

    @catch_exception
    async def upsert(self, data):
        raise NotImplementedError

    @catch_exception
    async def update_object(self, object_id, data):
        raise NotImplementedError

    @catch_exception
    async def update_object_field(self, object_id, data):
        raise NotImplementedError

    @catch_exception
    async def delete(self, object_id):
        raise NotImplementedError
