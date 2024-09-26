from typing import Any, List, Union

from app.common.dependencies.filters_input.base import BaseFiltersInput
from app.common.exceptions.catcher import catch_exception
from app.common.exceptions.repositories.base import BaseRepoError

# TODO: сделать в одну строку. Пусть длина импорта будет равна длина обычной строке
from app.common.exceptions.repositories.connection_refused import (
    ConnectionRefusedRepoError,
)
from app.common.exceptions.repositories.multiple_results import MultipleResultsRepoError
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.exceptions.repositories.wrong_query import WrongQueryError
from app.common.filtersets.base import BaseFiltersSet
from app.common.helpers.db import get_columns_by_table
from app.common.schemas.base import BaseSchema
from app.common.tables.base import BaseTable
from sqlalchemy import Result, Select, delete, insert, select, update
from sqlalchemy.exc import MultipleResultsFound, NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import Delete, ReturningInsert, Update


class BaseRepository:
    db_model = BaseTable

    one_read_schema = BaseSchema
    many_read_schema = BaseSchema
    create_schema = BaseSchema
    update_schema = BaseSchema

    filter_set = BaseFiltersSet

    catcher = catch_exception(base_error=BaseRepoError, description="repository exception")

    @catcher
    def __init__(self, session: AsyncSession):
        self.session = session

    @catcher
    async def execute(self, statement: Union[ReturningInsert, Select, Update, Delete]) -> Result:
        try:
            print(statement.compile(compile_kwargs={"literal_binds": True}))
            return await self.session.execute(statement)
        except ConnectionRefusedError:
            raise ConnectionRefusedRepoError
        except SQLAlchemyError:
            # TODO: 1) to logs
            # TODO: 2) SQLAlchemyError не такой содержательный, как если без него
            print(statement.compile(compile_kwargs={"literal_binds": True}))
            raise WrongQueryError

    @catcher
    def _create_query_for_getting_objects(self) -> Select:
        return select(get_columns_by_table(self.db_model))

    @catcher
    def _append_query_for_getting_objects(self, query: Select) -> Select:
        """For get_objects"""
        return query

    @catcher
    async def get_objects(
        self, raw_filters: BaseFiltersInput = BaseFiltersInput(), **add_filters
    ) -> List[many_read_schema]:
        filter_params = raw_filters.model_dump(exclude_none=True)
        filter_params.update(add_filters)

        query = self._create_query_for_getting_objects()
        query = self.filter_set(query).filter_query(filter_params)
        query = self._append_query_for_getting_objects(query)

        result = await self.execute(query)
        filtered_objects = result.all()
        return [self.many_read_schema.model_validate(obj) for obj in filtered_objects]

    @catcher
    async def get_object(self, **filters) -> one_read_schema:
        query = select(self.db_model).filter_by(**filters)
        result = await self.execute(query)
        try:
            obj = result.scalar_one()
        except NoResultFound:
            raise NotFoundRepoError
        except MultipleResultsFound:
            raise MultipleResultsRepoError
        return obj

    @catcher
    async def get_object_field(self, key: str, **filters) -> Any:
        query = select(getattr(self.db_model, key)).filter_by(**filters)  # TODO: обработать кейс, если key отсутствует
        result = await self.execute(query)
        value = result.scalar_one_or_none()  # TODO: обработать кейс, если по filters несколько строк подходит
        if value is None:
            raise NotFoundRepoError
        return value

    @catcher
    async def create(self, data: create_schema) -> one_read_schema:
        # TODO: можно ли упростить values(**data.model_dump()) - возможно, SQLModel решит проблему
        # TODO: вместо insert(self.db_model) можно написать только поля из read_schema (что эффективнее?)
        query = insert(self.db_model).values(**data.model_dump()).returning(self.db_model)
        result = await self.execute(query)
        await self.session.commit()
        obj = result.scalar_one()
        return obj

    @catcher
    async def create_bulk(self, data: List[create_schema]) -> List[many_read_schema]:
        raise NotImplementedError

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
    async def upsert(self, data):
        raise NotImplementedError

    @catcher
    async def update(self, data: update_schema, **filters) -> one_read_schema:
        query = (
            update(self.db_model)
            .filter_by(**filters)
            .values(**data.model_dump())
            .execution_options(populate_existing=True)  # TODO: Обновить SQLAlchemy до 2.0.36 для Computed полей
            .returning(self.db_model)
        )
        result = await self.execute(query)
        await self.session.commit()
        try:
            obj = result.scalar_one()
        except NoResultFound:
            raise NotFoundRepoError
        return obj

    @catcher
    async def update_bulk(self, data: update_schema, **filters) -> List[many_read_schema]:
        raise NotImplementedError

    @catcher
    async def update_object_field(self, object_id, data):
        raise NotImplementedError

    @catcher
    async def delete_object(self, **filters) -> one_read_schema:
        query = delete(self.db_model).filter_by(**filters).returning(self.db_model)
        result = await self.execute(query)
        await self.session.commit()
        try:
            obj = result.scalar_one()
        except NoResultFound:
            raise NotFoundRepoError
        return obj

    @catcher
    async def delete_bulk(self, **filters) -> List[many_read_schema]:
        raise NotImplementedError
