from typing import Sequence

from app.common.dependencies.api_args.base import BaseFilterSchema
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.type_error import RepoTypeError
from app.common.filtersets.base import BaseAsyncFilterSet
from app.common.schemas.base import BaseSchema
from app.common.tables.base import BaseTable
from sqlalchemy import insert, select
from sqlalchemy.exc import InvalidRequestError, MultipleResultsFound
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    db_model = BaseTable

    read_schema = BaseSchema
    create_schema = BaseSchema

    model_name = read_schema.__name__  # TODO: мб по-другому получать имя модели

    filter_set = BaseAsyncFilterSet
    filter_schema = BaseFilterSchema

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def catch_exception(method):
        async def wrapper(self, *args, **kwargs):
            try:
                return await method(self, *args, **kwargs)
            except TypeError as e:
                raise RepoTypeError(e, self.model_name, kwargs)
            except MultipleResultsFound as e:
                # Если хотим скаляр (одну строку), а под такие критерии подходит несколько
                raise BaseRepoError(e, self.model_name, kwargs)
            except InvalidRequestError as e:
                # Одно из пришедших полей отсутствует в таблице
                raise BaseRepoError(e, self.model_name, kwargs)
            except Exception as e:
                raise BaseRepoError(e, self.model_name, kwargs)  # TODO: какие данные стоит передавать в исключение

        return wrapper

    @catch_exception
    async def get_objects(self, raw_filters: filter_schema) -> Sequence[db_model]:  # TODO: возвращать нужно read_schema
        filter_set = self.filter_set(self.session, select(self.db_model))
        filter_params = raw_filters.model_dump(exclude_none=True)
        filtered_objects = await filter_set.filter(filter_params)
        return filtered_objects

    @catch_exception
    async def get_object(self, **kwargs) -> db_model:  # TODO: возвращать нужно read_schema
        query = select(self.db_model).filter_by(**kwargs)
        result = await self.session.execute(query)
        obj = result.scalar_one_or_none()
        return obj

    @catch_exception
    async def create(self, data: create_schema) -> db_model:  # TODO: возвращать нужно read_schema
        # TODO: sqlalchemy.exc.CompileError: Unconsumed column names: raw_password
        # TODO: можно ли сразу целиком строчку вернуть
        # TODO: можно ли упростить values(**data.model_dump())
        query = insert(self.db_model).values(**data.model_dump()).returning(self.db_model.id)
        result = await self.session.execute(query)
        object_id = result.scalar_one_or_none()
        await self.session.commit()
        return await self.get_object(id=object_id)

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
