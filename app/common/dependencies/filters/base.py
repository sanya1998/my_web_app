from copy import deepcopy
from types import UnionType
from typing import Dict, List, Set, Tuple, Type, Union, get_args, get_origin

from app.common.constants.order_by import PREFIX_DESC
from app.config.main import settings
from fastapi import Depends
from fastapi.params import Query
from pydantic import BaseModel, ConfigDict, Field, create_model
from sqlalchemy import Select, or_
from sqlalchemy.orm import DeclarativeBase
from typing_extensions import Self


class BaseFilters(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    _db_model = DeclarativeBase

    def set_db_model(self, model) -> Self:
        self._db_model = model
        return self

    class Helper:
        delimiter = "__"
        operator_eq = "eq"
        prefix_desc = PREFIX_DESC

        operators_execution = {
            operator_eq: lambda field, value: field == value,
            "neq": lambda field, value: field != value,
            "gt": lambda field, value: field > value,
            "ge": lambda field, value: field >= value,
            "lt": lambda field, value: field < value,
            "le": lambda field, value: field <= value,
            "between": lambda field, values: field.between(*values),
            "like": lambda field, value: field.like(value),
            "ilike": lambda field, value: field.ilike(value),
            "not_like": lambda field, value: field.notlike(value),
            "match": lambda field, value: field.match(value),
            "in": lambda field, value: field.in_(value),
            "not_in": lambda field, value: field.not_in(value),
            "is": lambda field, value: field.is_(value),
            "is_not": lambda field, value: field.is_not(value),
            "is_distinct_from": lambda field, value: field.is_distinct_from(value),
            "is_not_distinct_from": lambda field, value: field.isnot_distinct_from(value),
        }

    def get_where_clauses(self, _exclude_fields=None, **additional_filters) -> List:
        if _exclude_fields is None:
            _exclude_fields = set()

        where_clauses = []
        fields = dict(self)
        fields.update(additional_filters)
        for field_name, value in fields.items():
            if field_name in _exclude_fields:
                continue
            if isinstance(value, Query):
                value = value.default
            if value is None:
                continue
            if isinstance(value, BaseFilters):
                where_clauses.extend(value.get_where_clauses())
                continue
            if self.Helper.delimiter in field_name:
                field_name, operator = field_name.rsplit(self.Helper.delimiter, maxsplit=1)
            else:
                operator = self.Helper.operator_eq
            if operator not in self.Helper.operators_execution:
                continue
            if (field := getattr(self._db_model, field_name, None)) is None:
                continue
            clause = self.Helper.operators_execution[operator](field, value)
            where_clauses.append(clause)
        return where_clauses

    def modify_query(self, query: Select, _exclude_fields=None, **additional_filters) -> Select:
        """Добавляет фильтры к sqlalchemy-запросу"""
        for method in dir(self):
            if method.startswith("add__"):
                query = getattr(self, method)(query=query, _exclude_fields=_exclude_fields)

        if where_clauses := self.get_where_clauses(_exclude_fields, **additional_filters):
            query = query.where(*where_clauses)

        return query


class LimitOffsetFilters(BaseFilters):
    limit: int | None = Field(settings.LIMIT_DEFAULT, ge=1, le=settings.LIMIT_MAX)
    offset: int | None = Field(settings.OFFSET_DEFAULT, ge=0)

    def add__limit_offset(self, query: Select, _exclude_fields: Set = None) -> Select:
        if _exclude_fields is None:
            _exclude_fields = set()
        _exclude_fields.update({"limit", "offset"})
        return query.limit(self.limit).offset(self.offset)


class OrderByFilters(BaseFilters):
    order_by: Tuple | None = Field(Query(None))

    def add__order_by(self, query: Select, _exclude_fields: Set = None) -> Select:
        if _exclude_fields is None:
            _exclude_fields = set()
        _exclude_fields.add("order_by")

        if isinstance(self.order_by, Query):
            self.order_by = self.order_by.default
        if self.order_by:
            sort_fields = []
            for field_name in self.order_by:
                if field_name.startswith(self.Helper.prefix_desc):
                    field_name = field_name.removeprefix(self.Helper.prefix_desc)
                    direction = "desc"
                else:
                    direction = "asc"
                if not (field := getattr(self._db_model, field_name, None)):
                    continue

                field_with_direction = getattr(field, direction)()
                sort_fields.append(field_with_direction)
            query = query.order_by(*sort_fields)
        return query


class MainFilters(LimitOffsetFilters, OrderByFilters):
    pass


class SearchFilters(BaseFilters):
    search: str | None = None

    class Helper(BaseFilters.Helper):
        search_fields = list()

    def add__search_filter(self, query: Select, _exclude_fields: Set = None) -> Select:
        if _exclude_fields is None:
            _exclude_fields = set()
        _exclude_fields.add("search")

        if self.search:
            search_filters = []
            for field in self.Helper.search_fields:
                search_filters.append(field.ilike(f"%{self.search}%"))
            query = query.where(or_(*search_filters))
        return query


def filter_depends(filter_model: type[BaseFilters], *args, **kwargs):
    """
    Для свагера все входные параметры переходят на верхний уровень. К параметрам вложенных моделей добавляются префиксы.
    После получения входных данных параметры возвращаются на свои уровни без префиксов.
    """

    def prepare_annotation(annotation):
        if get_origin(annotation) in [Union, UnionType]:
            annotation_args = list(get_args(annotation))
            if type(None) in annotation_args:
                annotation_args.remove(type(None))
            annotation = annotation_args[0]
        annotation_class = annotation if isinstance(annotation, type) else type(annotation)
        return annotation, annotation_class

    def prepare_fields(prefix: str, filter_model_: Type[BaseFilters], swagger_fields_, field_map_):
        for name, f in filter_model_.model_fields.items():
            swagger_field_name = f"{prefix}{name}"
            annotation, annotation_class = prepare_annotation(f.annotation)
            if issubclass(annotation_class, BaseFilters):
                field_map_[name] = dict()
                prepare_fields(f"{swagger_field_name}_", annotation, swagger_fields_, field_map_[name])
            else:
                field_map_[name] = swagger_field_name
                swagger_fields_[swagger_field_name] = (f.annotation, deepcopy(f))
        return swagger_fields_, field_map_

    swagger_fields, field_map = prepare_fields("", filter_model, dict(), dict())
    swagger_model: type[BaseFilters] = create_model("swagger_model", **swagger_fields)

    class ForSwagger(swagger_model):
        def __new__(cls, *args_, **kwargs_):
            def go_deep(field_map_) -> Dict:
                return {k: go_deep(v) if isinstance(v, dict) else kwargs_[v] for k, v in field_map_.items()}

            return filter_model(**go_deep(field_map))

    return Depends(ForSwagger, *args, **kwargs)
