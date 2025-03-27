from typing import Any, List, TypeVar, Union

from app.common.dependencies.filters.base import BaseFilters
from app.common.dependencies.filters.export import ExportFilters
from app.common.exceptions.catcher import catch_exception
from app.common.exceptions.repositories.attribute import AttributeRepoError
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.connection_refused import ConnectionRefusedRepoError
from app.common.exceptions.repositories.multiple_results import MultipleResultsRepoError
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.exceptions.repositories.wrong_query import WrongQueryError
from app.common.helpers.db import get_columns_by_table
from app.common.schemas.base import BaseSchema
from app.common.tables.base import BaseTable
from sqlalchemy import Result, Select, delete, exists, insert, select, update
from sqlalchemy.exc import MultipleResultsFound, NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import Delete, ReturningInsert, Update


class BaseRepository:
    db_model = BaseTable

    one_read_schema = TypeVar("one_read_schema", bound=BaseSchema)
    many_read_schema = TypeVar("many_read_schema", bound=BaseSchema)
    one_created_read_schema = TypeVar("one_created_read_schema", bound=BaseSchema)
    many_created_read_schema = TypeVar("many_created_read_schema", bound=BaseSchema)
    one_updated_read_schema = TypeVar("one_updated_read_schema", bound=BaseSchema)
    many_updated_read_schema = TypeVar("many_updated_read_schema", bound=BaseSchema)
    upserted_read_schema = TypeVar("upserted_read_schema", bound=BaseSchema)
    one_deleted_read_schema = TypeVar("one_deleted_read_schema", bound=BaseSchema)
    many_deleted_read_schema = TypeVar("many_deleted_read_schema", bound=BaseSchema)

    create_schema = TypeVar("create_schema", bound=BaseSchema)
    update_schema = TypeVar("update_schema", bound=BaseSchema)
    filters_schema = TypeVar("filters_schema", bound=BaseFilters)

    catcher = catch_exception(
        base_error=BaseRepoError, description="Repository exception", warnings=[NotFoundRepoError]
    )

    @catcher
    def __init__(self, session: AsyncSession):
        self.session = session

    @catcher
    async def execute(self, query: Union[ReturningInsert, Select, Update, Delete]) -> Result:
        try:
            # print(query.compile(compile_kwargs={"literal_binds": True}))  # TODO: remove
            return await self.session.execute(query)
        except ConnectionRefusedError:
            raise ConnectionRefusedRepoError
        except SQLAlchemyError:
            # TODO: 1) to logs
            # TODO: 2) SQLAlchemyError не такой содержательный, как если без него
            print(query.compile(compile_kwargs={"literal_binds": True}))  # TODO: remove
            raise WrongQueryError

    @catcher
    def _modify_query_for_getting_objects(self, query: Select, filters: filters_schema, **additional_filters) -> Select:
        return query

    @catcher
    async def get_objects(self, filters: BaseFilters, **additional_filters) -> List[many_read_schema]:
        query = select(get_columns_by_table(self.db_model))
        query = self._modify_query_for_getting_objects(query, filters, **additional_filters)
        query = filters.modify_query(query, **additional_filters)
        result = await self.execute(query)
        filtered_objects = result.all()
        return [self.many_read_schema.model_validate(obj) for obj in filtered_objects]

    @catcher
    async def get_raw_objects(self, filters: ExportFilters, **additional_filters) -> Any:
        filters.set_db_model(self.db_model)
        query = filters.modify_query(select(self.db_model), **additional_filters)
        db_answer = await self.execute(query)
        data = db_answer.scalars().all()
        return data

    @catcher
    def _modify_query_for_getting_object(self, query: Select, **filters):
        return query

    @catcher
    async def get_object(self, **filters) -> one_read_schema:
        query = select(get_columns_by_table(self.db_model))
        query = BaseFilters().set_db_model(self.db_model).modify_query(query, **filters)
        query = self._modify_query_for_getting_object(query, **filters)
        result = await self.execute(query)
        try:
            obj = result.one()
        except NoResultFound:
            raise NotFoundRepoError
        except MultipleResultsFound:
            raise MultipleResultsRepoError
        return self.one_read_schema.model_validate(obj)

    @catcher
    async def get_object_field(self, key: str, **filters) -> Any:
        if (field := getattr(self.db_model, key, None)) is None:
            raise AttributeRepoError
        query = select(field).filter_by(**filters)
        result = await self.execute(query)
        try:
            return result.scalar_one()
        except MultipleResultsFound:
            raise MultipleResultsRepoError
        except NoResultFound:
            raise NotFoundRepoError

    @catcher
    async def create(self, data: create_schema) -> one_created_read_schema:
        # TODO: можно ли упростить values(**data.model_dump()) - возможно, SQLModel решит проблему
        query = insert(self.db_model).values(**data.model_dump()).returning(self.db_model)
        result = await self.execute(query)
        await self.session.commit()
        obj = result.scalar_one()
        return self.one_created_read_schema.model_validate(obj)

    @catcher
    async def create_bulk(self, data: List[create_schema]) -> List[many_created_read_schema]:
        raise NotImplementedError

    @catcher
    async def is_exists(self, **filters) -> bool:
        query = select(exists(select(self.db_model).filter_by(**filters)))
        result = await self.execute(query)
        value = result.scalar_one()
        return value

    @catcher
    async def is_not_exists(self, **filters) -> bool:
        return not (await self.is_exists(**filters))

    @catcher
    async def upsert(self, data) -> upserted_read_schema:
        raise NotImplementedError

    @catcher
    async def update(self, data: update_schema, **filters) -> one_updated_read_schema:
        query = update(self.db_model).filter_by(**filters).values(**data.model_dump()).returning(self.db_model)
        result = await self.execute(query)
        await self.session.commit()
        try:
            obj = result.scalar_one()
        except NoResultFound:
            raise NotFoundRepoError
        return self.one_updated_read_schema.model_validate(obj)

    @catcher
    async def update_bulk(self, data: update_schema, **filters) -> List[many_updated_read_schema]:
        raise NotImplementedError

    @catcher
    async def update_object_field(self, object_id, data):
        raise NotImplementedError

    @catcher
    async def delete_object(self, **filters) -> one_deleted_read_schema:
        query = delete(self.db_model).filter_by(**filters).returning(self.db_model)
        result = await self.execute(query)
        await self.session.commit()
        try:
            obj = result.scalar_one()
        except NoResultFound:
            raise NotFoundRepoError
        return self.one_deleted_read_schema.model_validate(obj)

    @catcher
    async def delete_bulk(self, **filters) -> List[many_deleted_read_schema]:
        raise NotImplementedError
