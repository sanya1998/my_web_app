# TODO: поработать с повторяющимися константами
# TODO: AsyncSearch().execute
# TODO: Подумать над более читаемыми способами (цепочка для формирования запроса)
from app.config.common import settings
from elasticsearch.dsl import AsyncSearch
from es.schemas.products import Color, ProductReadSchema, ProductShortReadSchema


async def test_match_query(es_client):
    """Тест Match запроса"""
    from elasticsearch.dsl.query import Match

    match_query = AsyncSearch().query(Match(category={"query": "smartphone", "fuzziness": "AUTO"}))[:5]
    result = await es_client.search(
        base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=match_query.to_dict(), response_model=ProductReadSchema
    )
    assert result.total == 17
    assert [source.id for source in result.sources] == ["6", "18", "36", "66", "24"]


async def test_term_query(es_client):
    """Тест Term запроса"""
    from elasticsearch.dsl.query import Term

    term_query = AsyncSearch().query(Term(category="smartphone"))[:3]
    result = await es_client.search(
        base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=term_query.to_dict(), response_model=ProductReadSchema
    )
    assert result.total == 17
    assert [source.id for source in result.sources] == ["6", "18", "36"]


async def test_range_query(es_client):
    """Тест Range запроса"""
    from elasticsearch.dsl.query import Range

    range_query = AsyncSearch().query(Range(base_price={"gte": 500, "lte": 1000}))[:3]

    result = await es_client.search(
        base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=range_query.to_dict(), response_model=ProductReadSchema
    )
    assert result.total == 14
    assert [source.id for source in result.sources] == ["7", "13", "43"]


async def test_complex_query_with_operators(es_client):
    """Тест комплексного запроса с операторами"""
    from elasticsearch.dsl.query import Bool, Match, MultiMatch, Range, Term

    # Способ через операторы (| и &)
    match_q = Match(product_name={"query": "phone"})
    multi_match_q = MultiMatch(query="wireless", fields=["product_name", "description", "features"])
    range_q = Range(base_price={"gte": 300, "lte": 1500})
    term_q = Term(is_available=True)

    # Используем операторы как в Python
    complex_with_operators_q = (match_q | multi_match_q) & range_q & term_q

    complex_with_operators = AsyncSearch().query(complex_with_operators_q)[:10]

    result_operators = await es_client.search(
        base_alias=settings.ES_PRODUCTS_BASE_ALIAS,
        body=complex_with_operators.to_dict(),
        response_model=ProductReadSchema,
    )

    # Тот же запрос через Bool явно
    complex_with_bool = AsyncSearch().query(
        Bool(
            should=[
                Match(product_name={"query": "phone"}),
                MultiMatch(
                    query="wireless",
                    fields=["product_name", "description", "features"],
                ),
            ],
            must=[
                Range(base_price={"gte": 300, "lte": 1500}),
                Term(is_available=True),
            ],
            minimum_should_match=1,
        )
    )[:10]

    result_bool = await es_client.search(
        base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=complex_with_bool.to_dict(), response_model=ProductReadSchema
    )

    assert result_bool.total == 4 == result_operators.total
    assert (
        [source.id for source in result_bool.sources]
        == ["23", "83", "53", "77"]
        == [source.id for source in result_operators.sources]
    )


async def test_aggregation_brands_analysis(es_client):
    """Тест агрегации по брендам"""
    from elasticsearch.dsl.aggs import Stats, Terms

    brands_analysis = AsyncSearch()[:0]  # size=0

    top_brands_k = "top_brands"
    price_stats_k = "price_stats"
    # Добавляем агрегации
    brands_analysis.aggs.bucket(top_brands_k, Terms(field="brand", size=5))
    brands_analysis.aggs.metric(price_stats_k, Stats(field="base_price"))

    result = await es_client.aggregate(base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=brands_analysis.to_dict())

    # Проверяем агрегацию по брендам
    buckets = result["aggregations"][top_brands_k]["buckets"]
    assert len(buckets) == 5
    assert [(bucket["doc_count"], bucket["key"]) for bucket in buckets] == [
        (17, "microsoft"),
        (16, "samsung"),
        (16, "sony"),
        (9, "apple"),
        (9, "dell"),
    ]

    # Проверяем статистику по ценам
    price_stats = result["aggregations"][price_stats_k]
    assert round(price_stats["avg"], 2) == 261.72
    assert round(price_stats["min"], 2) == 40.54
    assert round(price_stats["max"], 2) == 524.25


async def test_aggregation_price_analysis(es_client):
    """Тест агрегации по ценам"""
    from elasticsearch.dsl.aggs import Range as RangeAgg
    from elasticsearch.dsl.aggs import Stats
    from elasticsearch.dsl.query import Range

    # Аналитика ценовых диапазонов
    # Только агрегации, без документов
    price_analysis = AsyncSearch()[:0]

    # Добавляем фильтр по цене через Range запрос
    price_analysis = price_analysis.query(Range(base_price={"lte": 2000}))

    # Добавляем агрегации
    price_ranges_k = "price_ranges"
    rating_stats_k = "rating_stats"
    price_analysis.aggs.bucket(
        price_ranges_k,
        RangeAgg(
            field="base_price",
            ranges=[
                {"to": 500},
                {"from": 500, "to": 1000},
                {"from": 1000, "to": 2000},
            ],
        ),
    )
    price_analysis.aggs.metric(rating_stats_k, Stats(field="rating"))
    result = await es_client.aggregate(base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=price_analysis.to_dict())

    # Проверяем ценовые диапазоны
    price_ranges = result["aggregations"][price_ranges_k]["buckets"]
    assert len(price_ranges) == 3
    assert [bucket["doc_count"] for bucket in price_ranges] == [86, 14, 0]

    # Проверяем статистику по рейтингу
    rating_stats = result["aggregations"][rating_stats_k]
    assert round(rating_stats["avg"], 2) == 3.9
    assert round(rating_stats["min"], 2) == 3.0
    assert round(rating_stats["max"], 2) == 4.8


async def test_full_query_with_aggregations(es_client):
    """Тест полноценного запроса с агрегациями"""
    from elasticsearch.dsl.aggs import Stats, Terms
    from elasticsearch.dsl.query import MultiMatch

    # Полноценный запрос с агрегациями
    full_query = AsyncSearch()

    # Поисковый запрос
    full_query = full_query.query(
        MultiMatch(
            query="phone",
            fields=["product_name", "description"],
            fuzziness="AUTO",
        )
    )

    # Агрегации
    categories_k = "categories"
    brands_k = "brands"
    price_stats_k = "price_stats"
    full_query.aggs.bucket(categories_k, Terms(field="category", size=5))
    full_query.aggs.bucket(brands_k, Terms(field="brand", size=5))
    full_query.aggs.metric(price_stats_k, Stats(field="base_price"))

    # Ограничиваем результаты
    full_query = full_query[:8]

    # Выбираем только нужные поля
    full_query = full_query.source(includes=["product_name", "description", "base_price", "rating", "brand"])

    result = await es_client.aggregate(base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=full_query.to_dict())

    assert len(result["hits"]["hits"]) == 2
    assert "aggregations" in result

    # Проверяем агрегации
    categories = result["aggregations"][categories_k]["buckets"]
    brands = result["aggregations"][brands_k]["buckets"]
    price_stats = result["aggregations"][price_stats_k]

    assert len(categories) > 0
    assert len(brands) > 0
    assert "avg" in price_stats


async def test_stats_query(es_client):
    """Тест запроса общей статистики"""
    from elasticsearch.dsl.aggs import Cardinality, Stats

    # Общая статистика
    stats_query = AsyncSearch()[:0]  # size=0, только агрегации

    # Добавляем агрегации
    total_categories_k = "total_categories"
    total_brands_k = "total_brands"
    global_stats_k = "global_stats"

    stats_query.aggs.metric(total_categories_k, Cardinality(field="category"))
    stats_query.aggs.metric(total_brands_k, Cardinality(field="brand"))
    stats_query.aggs.metric(global_stats_k, Stats(field="base_price"))

    result = await es_client.aggregate(base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=stats_query.to_dict())

    categories_count = result["aggregations"][total_categories_k]["value"]
    brands_count = result["aggregations"][total_brands_k]["value"]
    avg_price = result["aggregations"][global_stats_k]["avg"]

    assert int(categories_count) == 6  # Все категории
    assert int(brands_count) == 9  # Все бренды
    assert round(avg_price, 2) == 261.72


async def test_nested_aggregation(es_client):
    """Тест nested агрегаций"""
    from elasticsearch.dsl.aggs import Filter, Nested, Stats, Terms
    from elasticsearch.dsl.query import Range

    # Nested агрегации
    nested_analysis = AsyncSearch().extra(size=0)

    # Создаем nested агрегацию (без name в конструкторе!)
    nested_agg = Nested(path="variants")

    # Внутри nested добавляем filter агрегацию
    filter_agg = Filter(filter=Range(variants__stock={"gt": 0}))

    # Внутри filter агрегации добавляем другие агрегации
    filter_agg.bucket("colors", Terms(field="variants.color", size=3))
    filter_agg.metric("price_stats", Stats(field="variants.price_modifier"))

    # Собираем цепочку
    nested_agg.bucket("available_variants", filter_agg)
    nested_analysis.aggs.bucket("variants_in_stock", nested_agg)

    result = await es_client.aggregate(base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=nested_analysis.to_dict())

    # Получаем данные из сложной структуры ответа
    data = result["aggregations"]["variants_in_stock"]["available_variants"]
    buckets = data["colors"]["buckets"]

    assert data["doc_count"] == 97
    assert len(buckets) == 3
    assert [(bucket["doc_count"], bucket["key"]) for bucket in buckets] == [(15, "silver"), (14, "black"), (14, "blue")]


async def test_nested_query(es_client):
    """Тест nested запросов"""
    from elasticsearch.dsl.query import Bool, Nested, Range

    # Nested запросы
    nested_query = AsyncSearch().query(
        Nested(
            path="variants",
            query=Bool(
                must=[
                    Range(variants__stock={"gt": 0}),
                    Range(variants__price_modifier={"gt": 0}),
                ]
            ),
            score_mode="none",
        )
    )[:15]

    result = await es_client.search(
        base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=nested_query.to_dict(), response_model=ProductShortReadSchema
    )

    assert result.total == 44
    for hit in result.sources:
        assert any(variant.stock > 0 and variant.price_modifier > 0 for variant in hit.variants)


async def test_computed_fields(es_client):
    """Тест вычисляемых полей на клиенте"""
    from elasticsearch.dsl.query import Match

    search_query = AsyncSearch().query(Match(category={"query": "laptop"}))[:1]

    result = await es_client.search(
        base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=search_query.to_dict(), response_model=ProductReadSchema
    )

    assert result.total == 17
    source = result.sources[0]

    # Проверка computed полей (они вычисляются в Pydantic модели)
    assert source.total_stock == 13
    assert source.min_price == 483.25
    assert source.max_price == 504.75
    assert source.available_colors == [Color.BLUE]
    assert source.has_variants is True

    print("✅ Все computed поля работают на клиенте!")
    print(f"total_stock: {source.total_stock}")
    print(f"min_price: {source.min_price}")
    print(f"max_price: {source.max_price}")
    print(f"available_colors: {source.available_colors}")
    print(f"price_range: {source.price_range}")
