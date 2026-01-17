from typing import Annotated

from app.api.data.products.filters import ProductCommonParams
from elasticsearch import AsyncElasticsearch
from elasticsearch.dsl import AsyncSearch
from elasticsearch.dsl.query import Bool, MultiMatch, Nested, Range, Term, Terms
from es.clients.pydantic_ import PydanticESClient
from fastapi import Query
from starlette.requests import Request


def get_pydantic_es_client(request: Request) -> PydanticESClient:
    """Зависимость для получения клиента Elasticsearch"""
    return request.app.state.pydantic_es_client


def get_es_client(request: Request) -> AsyncElasticsearch:
    """Зависимость для получения клиента Elasticsearch"""
    return request.app.state.es_client


def build_search_query(
    params: Annotated[ProductCommonParams, Query()],
) -> AsyncSearch:
    """
    Построить поисковый запрос для товаров на основе параметров фильтрации

    Использует официальный elasticsearch.dsl для построения запросов.

    Args:
        params: Параметры фильтрации из Query параметров

    Returns:
        Search: Поисковый запрос elasticsearch-dsl
    """
    search = AsyncSearch()

    must_queries = []  # Для полнотекстового поиска (влияет на score)
    filter_queries = []  # Для точных фильтров (не влияет на score)

    # 1. Текстовый поиск (добавляем в must для влияния на score)
    if params.search_query:
        must_queries.append(
            MultiMatch(
                query=params.search_query, fields=["product_name", "description", "brand", "features"], fuzziness="AUTO"
            )
        )

    # 2. Точные фильтры (добавляем в filter для скорости)

    # Категории
    if params.categories:
        filter_queries.append(Terms(category=params.categories))

    # Бренды
    if params.brands:
        filter_queries.append(Terms(brand=params.brands))

    # Цена
    price_range = {}
    if params.min_price is not None:
        price_range["gte"] = params.min_price
    if params.max_price is not None:
        price_range["lte"] = params.max_price
    if price_range:
        filter_queries.append(Range(base_price=price_range))

    # Рейтинг
    if params.min_rating is not None:
        filter_queries.append(Range(rating={"gte": params.min_rating}))

    # Наличие
    if params.is_available is not None:
        filter_queries.append(Term(is_available=params.is_available))

    # Скидка
    if params.is_on_sale is not None:
        filter_queries.append(Term(is_on_sale=params.is_on_sale))

    # Теги
    if params.tags:
        filter_queries.append(Terms(tags=params.tags))

    # Фичи
    if params.features:
        filter_queries.append(Terms(features=params.features))

    # Цвета (nested поле) - используем правильный синтаксис
    if params.colors:
        filter_queries.append(Nested(path="variants", query=Terms(variants__color=params.colors)))

    # 3. Собираем финальный Bool запрос
    bool_query = Bool()
    if must_queries:
        bool_query.must = must_queries
    if filter_queries:
        bool_query.filter = filter_queries
    search = search.query(bool_query)

    # 4. Пагинация
    search = search[(params.page - 1) * params.per_page : params.page * params.per_page]

    # 5. Сортировка
    search = search.sort({params.sort_field: {"order": params.order}})

    return search
