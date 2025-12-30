from typing import Annotated

from app.api.data.products.filters import ProductCommonParams
from es.clients.pydantic_ import PydanticESClient
from es.main_query.main import MainQuery
from es.main_query.query import Bool, MatchAll, MultiMatch, NestedQuery, Range, Term, Terms
from fastapi import Query
from starlette.requests import Request


def get_es_client(request: Request) -> PydanticESClient:
    """Зависимость для получения клиента Elasticsearch"""
    return request.app.state.es_client


def build_main_query(
    params: Annotated[ProductCommonParams, Query()],
):
    query_parts = []

    # Текстовый поиск
    if params.search_query:
        query_parts.append(
            MultiMatch(
                query=params.search_query,
                fields=["product_name", "description", "brand", "features"],
                fuzziness="AUTO",
            )
        )

    # Фильтр по категориям
    if params.categories:
        query_parts.append(Terms(field="category", values=[c.value for c in params.categories]))

    # Фильтр по брендам
    if params.brands:
        query_parts.append(Terms(field="brand", values=params.brands))

    # Фильтр по цене TODO: упростить до Range(field="base_price", lte=..., gte=...)
    price_range = {}
    if params.min_price is not None:
        price_range["gte"] = params.min_price
    if params.max_price is not None:
        price_range["lte"] = params.max_price
    if price_range:
        query_parts.append(Range(field="base_price", **price_range))

    # Фильтр по рейтингу
    if params.min_rating is not None:
        query_parts.append(Range(field="rating", gte=params.min_rating))

    # Фильтр по наличию
    if params.is_available is not None:
        query_parts.append(Term(field="is_available", value=params.is_available))

    # Фильтр по скидке
    if params.is_on_sale is not None:
        query_parts.append(Term(field="is_on_sale", value=params.is_on_sale))

    # Фильтр по тегам
    if params.tags:
        query_parts.append(Terms(field="tags", values=params.tags))

    # Фильтр по фичам
    if params.features:
        query_parts.append(Terms(field="features", values=params.features))

    # Фильтр по цветам (из вариантов)
    if params.colors:
        # Для фильтрации по nested полям нужен nested query
        query_parts.append(NestedQuery(path="variants", query=Terms(field="variants.color", values=params.colors)))

    # Собираем финальный запрос
    if query_parts:
        search_query = Bool(_must=query_parts)
    else:
        search_query = MatchAll()

    # Создаем MainQuery
    main_query = (
        MainQuery(query=search_query)
        .paginate(page=params.page, per_page=params.per_page)
        .sort(params.sort_field, params.order)
    )
    return main_query
