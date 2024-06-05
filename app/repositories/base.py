import asyncio
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, List

from app.common.dependencies.api_args.base import BaseFilterSchema
from app.common.exceptions.repositories.base import BaseRepoError
from app.common.exceptions.repositories.not_found import NotFoundRepoError
from app.common.filtersets.base import BaseAsyncFilterSet
from app.common.schemas.base import BaseSchema
from app.common.tables.base import BaseTable
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    db_model = BaseTable

    read_schema = BaseSchema
    create_schema = BaseSchema

    filter_set = BaseAsyncFilterSet
    filter_schema = BaseFilterSchema

    @staticmethod
    def catch_exception(method: Callable) -> Callable:
        @contextmanager
        def wrapping_logic(self, *args, **kwargs):
            try:
                yield
            except Exception as ex:
                # TODO: Эти исключения уже ловились. Надо подумать, как с ними работать
                #  + ConnectionRefusedError (когда бд отключена)
                # except MultipleResultsFound as e:
                #     # Если хотим скаляр (одну строку), а под такие критерии подходит несколько
                #     raise BaseRepoError(e, self.model_name, kwargs)
                # except InvalidRequestError as e:
                #     # Одно из пришедших полей отсутствует в таблице
                #     raise BaseRepoError(e, self.model_name, kwargs)
                # except CompileError as e:
                #     # Если при создании придет поле, которого нет в таблице. (по идее должно решиться SQLModel)
                #     raise BaseRepoError(e, self.model_name, kwargs)
                class UnitingException(ex.__class__, BaseRepoError):
                    """
                    Наследование от BaseRepoError позволяет ловить все исключения из репозитория.
                    ex.__class__ содержит информацию о типе ошибке.
                    method_args, method_kwargs - входные данные.
                    """

                    method_args = args
                    method_kwargs = kwargs

                message = f"{ex.__class__.__name__}: {ex}.\nRepository exception from {self.model_name}."
                print(message)  # TODO: весь трейс в логи logger, sentry etc
                raise UnitingException(message) from ex

        @wraps(method)  # TODO: узнать, зачем это
        def wrapper(self, *args, **kwargs):
            if asyncio.iscoroutinefunction(method):

                async def async_wrapper():
                    with wrapping_logic(self, *args, **kwargs):
                        return await method(self, *args, **kwargs)

                return async_wrapper()
            else:
                with wrapping_logic(self, *args, **kwargs):
                    return method(self, *args, **kwargs)

        return wrapper

    @catch_exception
    def __init__(self, session: AsyncSession):
        self.model_name = self.__class__.__name__
        self.session = session

    @catch_exception
    async def get_objects(self, raw_filters: filter_schema) -> List[read_schema]:
        filter_set = self.filter_set(self.session, select(self.db_model))
        filter_params = raw_filters.model_dump(exclude_none=True)
        filtered_objects = await filter_set.filter(filter_params)
        return [self.read_schema.model_validate(obj) for obj in filtered_objects]

    @catch_exception
    async def get_object(self, **filters) -> read_schema:
        query = select(self.db_model).filter_by(**filters)
        result = await self.session.execute(query)
        obj = result.scalar_one_or_none()
        if obj is None:
            raise NotFoundRepoError
        return self.read_schema.model_validate(obj)

    @catch_exception
    async def get_object_field(self, key: str, **filters) -> Any:
        query = select(getattr(self.db_model, key)).filter_by(**filters)  # TODO: обработать кейс, если key отсутствует
        result = await self.session.execute(query)
        value = result.scalar_one_or_none()
        if value is None:
            raise NotFoundRepoError
        return value

    @catch_exception
    async def create(self, data: create_schema) -> read_schema:
        # TODO: можно ли упростить values(**data.model_dump()) - возможно, SQLModel решит проблему
        # TODO: вместо insert(self.db_model) можно написать только поля из read_schema (что эффективнее?)
        query = insert(self.db_model).values(**data.model_dump()).returning(self.db_model)
        result = await self.session.execute(query)
        obj = result.scalar_one()
        await self.session.commit()
        return self.read_schema.model_validate(obj)

    @catch_exception
    async def is_exists(self, **filters) -> bool:
        # TODO: можно ли упростить query
        query = select(self.db_model).filter_by(**filters).exists().select()
        result = await self.session.execute(query)
        value = result.scalar_one()
        return value

    @catch_exception
    async def is_not_exists(self, **filters) -> bool:
        return not (await self.is_exists(**filters))

    @catch_exception
    async def create_bulk(self, data: List[create_schema]) -> List[read_schema]:
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
