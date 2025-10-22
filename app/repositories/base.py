import io
from typing import Any, List, TypeVar, Union

from app.common.helpers.db import get_columns_by_table
from app.common.logger import logger
from app.common.schemas.base import BaseSchema
from app.common.tables.base import BaseTable
from app.config.common import settings
from app.dependencies.filters import BaseFilters, ExportFilters
from app.exceptions.catcher.catcher import catch_exception
from app.exceptions.repositories import (
    AlreadyExistsRepoError,
    AttributeRepoError,
    BaseRepoError,
    ConnectionRefusedRepoError,
    MultipleResultsRepoError,
    NotFoundRepoError,
)
from app.exceptions.repositories.integrity import IntegrityRepoError
from app.exceptions.repositories.programming import ProgrammingRepoError
from asyncpg import UniqueViolationError
from fastapi import UploadFile
from sqlalchemy import Result, Select, TextClause, delete, exists, func, select, text, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError, MultipleResultsFound, NoResultFound, ProgrammingError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import Delete, ReturningInsert, Update


class BaseRepository:
    db_model = BaseTable

    one_read_schema = TypeVar("one_read_schema", bound=BaseSchema)
    many_read_schema = TypeVar("many_read_schema", bound=BaseSchema)
    one_created_schema = TypeVar("one_created_schema", bound=BaseSchema)
    many_created_schema = TypeVar("many_created_schema", bound=BaseSchema)
    one_updated_schema = TypeVar("one_updated_schema", bound=BaseSchema)
    many_updated_schema = TypeVar("many_updated_schema", bound=BaseSchema)
    upserted_schema = TypeVar("upserted_schema", bound=BaseSchema)
    many_upserted_schema = TypeVar("many_upserted_schema", bound=BaseSchema)
    one_deleted_schema = TypeVar("one_deleted_schema", bound=BaseSchema)
    many_deleted_schema = TypeVar("many_deleted_schema", bound=BaseSchema)

    create_schema = TypeVar("create_schema", bound=BaseSchema)
    update_schema = TypeVar("update_schema", bound=BaseSchema)
    upsert_schema = TypeVar("upsert_schema", bound=BaseSchema)
    patch_schema = TypeVar("patch_schema", bound=BaseSchema)
    filters_schema = TypeVar("filters_schema", bound=BaseFilters)

    catcher = catch_exception(
        base_error=BaseRepoError,
        description="Repository exception",
        skips=[IntegrityError, ProgrammingError],
        warnings=[NotFoundRepoError, AlreadyExistsRepoError, IntegrityRepoError, ProgrammingRepoError],
    )

    @catcher
    def __init__(self, session: AsyncSession):
        self.session = session

    @catcher
    async def execute(self, query: Union[ReturningInsert, Select, Update, Delete, TextClause]) -> Result:
        try:
            # logger.info(query.compile(compile_kwargs={"literal_binds": True}))  # TODO: remove
            return await self.session.execute(query)
        except ConnectionRefusedError:
            raise ConnectionRefusedRepoError
        except SQLAlchemyError as ex:
            logger.warning(f"{repr(ex)}")
            # TODO: 2) SQLAlchemyError не такой содержательный, как если без него
            raise

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
    async def configure_autoincrement(self):
        # TODO: можно ли это сделать силами sqlalchemy ?
        table_name = self.db_model.__table__
        id_ = self.db_model.id.key
        pg_get_serial_sequence = f"pg_get_serial_sequence('{table_name}', '{id_}')"
        select_max = f"(SELECT MAX({id_}) FROM {table_name})"
        final_query = f"SELECT setval({pg_get_serial_sequence}, {select_max});"
        await self.execute(text(final_query))

    @catcher
    async def _get_driver_connection(self):
        # TODO: не нужно ли тут что-либо закрывать?
        connection = await self.session.connection()
        raw_connection = await connection.get_raw_connection()
        driver_connection = raw_connection.driver_connection
        return driver_connection

    @catcher
    async def export_all(self):
        driver_connection = await self._get_driver_connection()
        stream = io.BytesIO()
        await driver_connection.copy_from_table(
            self.db_model.__tablename__,
            output=stream,
            format=settings.FILE_FORMAT,
            encoding=settings.FILE_ENCODING,
            header=True,
        )
        stream.seek(0)
        return stream

    @catcher
    def _prepare_query_by_export(self, filters: ExportFilters, **additional_filters):
        """
        Можно было бы экранировать параметры (Все `:params_i` заменить на `$i`).
        copy_from_query позволяет передавать аргументы.
        Но сложности возникают из-за того, что при использовании в фильтрах списка появляется `(__[POSTCOMPILE_var_1])'
        """
        filters.set_db_model(self.db_model)
        query = filters.modify_query(select(self.db_model), **additional_filters)
        query_sql = str(query.compile(compile_kwargs={"literal_binds": True}))
        return query_sql

    @catcher
    async def export_filtered(self, filters: ExportFilters, **additional_filters):
        query_sql = self._prepare_query_by_export(filters, **additional_filters)
        driver_connection = await self._get_driver_connection()
        stream = io.BytesIO()
        await driver_connection.copy_from_query(
            query_sql, output=stream, format=settings.FILE_FORMAT, encoding=settings.FILE_ENCODING, header=True
        )
        stream.seek(0)
        return stream

    @catcher
    async def import_(self, file: UploadFile):
        driver_connection = await self._get_driver_connection()
        try:
            await driver_connection.copy_to_table(
                self.db_model.__tablename__,
                source=file.file,
                header=True,
                format=settings.FILE_FORMAT,
                encoding=settings.FILE_ENCODING,
            )
        except UniqueViolationError:
            raise AlreadyExistsRepoError
        await self.configure_autoincrement()
        await self.session.commit()

    @catcher
    def _modify_query_for_getting_object(self, query: Select, **filters):
        return query

    @catcher
    async def _get_object(self, **filters):
        query = select(get_columns_by_table(self.db_model))
        query = BaseFilters().set_db_model(self.db_model).modify_query(query, **filters)
        query = self._modify_query_for_getting_object(query, **filters)
        result = await self.execute(query)
        return result

    @catcher
    async def get_object(self, **filters) -> one_read_schema:
        result = await self._get_object(**filters)
        try:
            obj = result.one()
        except NoResultFound:
            raise NotFoundRepoError
        except MultipleResultsFound:
            raise MultipleResultsRepoError
        return self.one_read_schema.model_validate(obj)

    @catcher
    async def get_object_or_none(self, **filters) -> one_read_schema | None:
        result = await self._get_object(**filters)
        try:
            obj = result.one_or_none()
        except MultipleResultsFound:
            raise MultipleResultsRepoError
        return self.one_read_schema.model_validate(obj) if obj else None

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
    def _modify_query_for_creating_object(self, query, data):
        return query

    @catcher
    async def create(self, data: create_schema) -> one_created_schema:
        query = insert(self.db_model).values(**data.model_dump(exclude_none=True)).returning(self.db_model)
        query = self._modify_query_for_creating_object(query, data)
        try:
            result = await self.execute(query)
        except IntegrityError:
            # Нарушены индекс уникальности или уникальность поля, либо некорректный sql-запросе.
            raise IntegrityRepoError
        await self.session.commit()
        obj = result.scalar_one()
        return self.one_created_schema.model_validate(obj)

    @catcher
    async def create_bulk(self, data: List[create_schema]) -> List[many_created_schema]:
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
    async def upsert(self, data: upsert_schema, index_elements: list = None) -> upserted_schema:
        if not index_elements:
            index_elements = [self.db_model.id]
        data_dict = data.model_dump()
        set_dict = {**data_dict}

        #  При on_conflict_do_update не вызывается то, что указали в onupdate. TODO: не универсально
        if hasattr(self.db_model, "updated_dt"):
            set_dict["updated_dt"] = func.now()

        query = (
            insert(self.db_model)
            .values(**data_dict)
            .on_conflict_do_update(index_elements=index_elements, set_=set_dict)
            .returning(self.db_model)
        )
        try:
            result = await self.execute(query)
        except ProgrammingError:
            # Скорее всего, поле не настроено уникальным, по которому проверяется наличие записи
            raise ProgrammingRepoError
        await self.session.commit()
        obj = result.scalar_one()
        return self.upserted_schema.model_validate(obj)

    @catcher
    async def upsert_bulk(self, data: upsert_schema, index_elements: list = None) -> List[many_upserted_schema]:
        raise NotImplementedError

    @catcher
    async def _update(self, _exclude_unset, data: Union[update_schema, patch_schema], **filters) -> one_updated_schema:
        query = (
            update(self.db_model)
            .filter_by(**filters)
            .values(**data.model_dump(exclude_unset=_exclude_unset))
            .returning(self.db_model)
        )
        result = await self.execute(query)
        await self.session.commit()
        try:
            obj = result.scalar_one()
        except NoResultFound:
            raise NotFoundRepoError
        # TODO: не нужно ли это тоже использовать?
        # except MultipleResultsFound:
        #     raise MultipleResultsRepoError
        return self.one_updated_schema.model_validate(obj)

    @catcher
    async def update(self, data: update_schema, **filters) -> one_updated_schema:
        return await self._update(_exclude_unset=False, data=data, **filters)

    @catcher
    async def update_bulk(self, data: List[update_schema], **filters) -> List[many_updated_schema]:
        raise NotImplementedError

    @catcher
    async def update_object_fields(self, data: patch_schema, **filters):
        return await self._update(_exclude_unset=True, data=data, **filters)

    @catcher
    async def delete_object(self, **filters) -> one_deleted_schema:
        query = delete(self.db_model).filter_by(**filters).returning(self.db_model)
        result = await self.execute(query)
        await self.session.commit()
        try:
            obj = result.scalar_one()
        except NoResultFound:
            raise NotFoundRepoError
        return self.one_deleted_schema.model_validate(obj)

    @catcher
    async def delete_bulk(self, **filters) -> List[many_deleted_schema]:
        raise NotImplementedError

    @catcher
    async def truncate(self) -> List[many_deleted_schema]:
        raise NotImplementedError
