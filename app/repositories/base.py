from typing import Any, List

from app.common.dependencies.filters.base import BaseFiltersSchema
from app.common.exceptions.catcher import catch_exception
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.connection_refused import (
    ConnectionRefusedRepoError,
)
from app.common.exceptions.repositories.multiple_results import MultipleResultsRepoError
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.filtersets.base import BaseFiltersSet
from app.common.schemas.base import BaseSchema
from app.common.tables.base import BaseTable
from sqlalchemy import Executable, Result, insert, select
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    db_model = BaseTable

    read_schema = BaseSchema
    create_schema = BaseSchema

    filter_set = BaseFiltersSet

    catcher = catch_exception(base_error=BaseRepoError, description="repository exception")

    @catcher
    def __init__(self, session: AsyncSession):
        self.session = session

    @catcher
    async def execute(self, statement: Executable) -> Result:
        try:
            return await self.session.execute(statement)
        except ConnectionRefusedError:
            raise ConnectionRefusedRepoError

    @catcher
    async def get_objects(
        self, raw_filters: BaseFiltersSchema = BaseFiltersSchema(), **add_filters
    ) -> List[read_schema]:
        filter_params = raw_filters.model_dump(exclude_none=True)
        filter_params.update(add_filters)
        query = self.filter_set(select(self.db_model)).filter_query(filter_params)
        result = await self.execute(query)
        filtered_objects = result.scalars().all()
        return [self.read_schema.model_validate(obj) for obj in filtered_objects]

    @catcher
    async def get_object(self, **filters) -> read_schema:
        query = select(self.db_model).filter_by(**filters)
        result = await self.execute(query)
        try:
            obj = result.scalar_one()
        except NoResultFound:
            raise NotFoundRepoError
        except MultipleResultsFound:
            raise MultipleResultsRepoError
        return self.read_schema.model_validate(obj)

    @catcher
    async def get_object_field(self, key: str, **filters) -> Any:
        query = select(getattr(self.db_model, key)).filter_by(**filters)  # TODO: обработать кейс, если key отсутствует
        result = await self.execute(query)
        value = result.scalar_one_or_none()  # TODO: обработать кейс, если по filters несколько строк подходит
        if value is None:
            raise NotFoundRepoError
        return value

    @catcher
    async def create(self, data: create_schema) -> read_schema:
        # TODO: можно ли упростить values(**data.model_dump()) - возможно, SQLModel решит проблему
        # TODO: вместо insert(self.db_model) можно написать только поля из read_schema (что эффективнее?)
        query = insert(self.db_model).values(**data.model_dump()).returning(self.db_model)
        result = await self.execute(query)
        obj = result.scalar_one()
        await self.session.commit()
        return self.read_schema.model_validate(obj)

    @catcher
    async def is_exists(self, **filters) -> bool:
        # TODO: можно ли упростить query
        query = select(self.db_model).filter_by(**filters).exists().select()
        result = await self.execute(query)
        value = result.scalar_one()
        return value

    @catcher
    async def is_not_exists(self, **filters) -> bool:
        # TODO: not перенести из python в sql
        return not (await self.is_exists(**filters))

    @catcher
    async def create_bulk(self, data: List[create_schema]) -> List[read_schema]:
        raise NotImplementedError

    @catcher
    async def upsert(self, data):
        raise NotImplementedError

    @catcher
    async def update_object(self, object_id, data):
        raise NotImplementedError

    @catcher
    async def update_object_field(self, object_id, data):
        raise NotImplementedError

    @catcher
    async def delete(self, object_id):
        raise NotImplementedError
