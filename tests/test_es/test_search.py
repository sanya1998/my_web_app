# TODO: поработать с повторяющимися константами
from app.config.common import settings
from es.schemas.products import Color, ProductReadSchema, ProductShortReadSchema


async def test_match_query(es_client):
    """Тест Match запроса"""
    from es.main_query.main import MainQuery
    from es.main_query.query import Match

    # TODO:
    #  from elasticsearch.dsl.query import Match
    # Match запрос
    match_query = MainQuery(
        query=Match(query="smartphone", field="category", fuzziness="AUTO"),
        size=5,
    )

    result = await es_client.search(
        base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=match_query(), response_model=ProductReadSchema
    )
    assert result.total == 17
    assert [source.id for source in result.sources] == ["6", "18", "36", "66", "24"]


async def test_term_query(es_client):
    """Тест Term запроса"""
    from es.main_query.main import MainQuery
    from es.main_query.query import Term

    # Term запрос
    term_query = MainQuery(query=Term(field="category", value="smartphone"), size=3)

    result = await es_client.search(
        base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=term_query(), response_model=ProductReadSchema
    )
    assert result.total == 17
    assert [source.id for source in result.sources] == ["6", "18", "36"]


async def test_range_query(es_client):
    """Тест Range запроса"""
    from es.main_query.main import MainQuery
    from es.main_query.query import Range

    # Range запрос
    range_query = MainQuery(query=Range(field="base_price", gte=500, lte=1000), size=3)

    result = await es_client.search(
        base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=range_query(), response_model=ProductReadSchema
    )
    assert result.total == 14
    assert [source.id for source in result.sources] == ["7", "13", "43"]


async def test_complex_query_with_operators(es_client):
    """Тест комплексного запроса с операторами"""
    from es.main_query.main import MainQuery
    from es.main_query.query import Bool, Match, MultiMatch, Range, Term

    # С операторами
    complex_with_operators = MainQuery(
        query=(
            Match(query="phone", field="product_name")
            | MultiMatch(query="wireless", fields=["product_name", "description", "features"])
        )
        & Range(field="base_price", gte=300, lte=1500)
        & Term(field="is_available", value=True),
        size=10,
    )

    result_operators = await es_client.search(
        base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=complex_with_operators(), response_model=ProductReadSchema
    )

    # Тот же запрос через Bool
    complex_with_bool = MainQuery(
        query=Bool(
            _should=[
                Match(query="phone", field="product_name"),
                MultiMatch(
                    query="wireless",
                    fields=["product_name", "description", "features"],
                ),
            ],
            _must=[
                Range(field="base_price", gte=300, lte=1500),
                Term(field="is_available", value=True),
            ],
            minimum_should_match=1,
        ),
        size=10,
    )

    result_bool = await es_client.search(
        base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=complex_with_bool(), response_model=ProductReadSchema
    )
    assert result_bool.total == 4 == result_operators.total
    assert (
        [source.id for source in result_bool.sources]
        == ["23", "83", "53", "77"]
        == [source.id for source in result_operators.sources]
    )


async def test_aggregation_brands_analysis(es_client):
    """Тест агрегации по брендам"""
    from es.main_query.aggregation import StatsAgg, TermsAgg
    from es.main_query.main import MainQuery

    # Аналитика по брендам
    brands_analysis = MainQuery(
        aggs=[
            TermsAgg("top_brands", "brand", size=5),
            StatsAgg("price_stats", "base_price"),
        ],
        size=0,
    )

    result = await es_client.aggregate(base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=brands_analysis())

    # Проверяем агрегацию по брендам
    buckets = result["aggregations"]["top_brands"]["buckets"]
    assert len(buckets) == 5
    assert [(bucket["doc_count"], bucket["key"]) for bucket in buckets] == [
        (17, "microsoft"),
        (16, "samsung"),
        (16, "sony"),
        (9, "apple"),
        (9, "dell"),
    ]

    # Проверяем статистику по ценам
    price_stats = result["aggregations"]["price_stats"]
    assert round(price_stats["avg"], 2) == 261.72
    assert round(price_stats["min"], 2) == 40.54
    assert round(price_stats["max"], 2) == 524.25


async def test_aggregation_price_analysis(es_client):
    """Тест агрегации по ценам"""
    from es.main_query.aggregation import RangeAgg, StatsAgg
    from es.main_query.main import MainQuery
    from es.main_query.query import Range as RangeQuery

    # Аналитика ценовых диапазонов
    price_analysis = (
        MainQuery()
        .query(RangeQuery(field="base_price", lte=2000))
        .add_agg(
            RangeAgg(
                "price_ranges",
                "base_price",
                [
                    {"to": 500},
                    {"from": 500, "to": 1000},
                    {"from": 1000, "to": 2000},
                ],
            )
        )
        .add_agg(StatsAgg("rating_stats", "rating"))
        .size(0)
    )

    result = await es_client.aggregate(base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=price_analysis())

    # Проверяем ценовые диапазоны
    price_ranges = result["aggregations"]["price_ranges"]["buckets"]
    assert len(price_ranges) == 3
    assert [bucket["doc_count"] for bucket in price_ranges] == [86, 14, 0]

    # Проверяем статистику по рейтингу
    rating_stats = result["aggregations"]["rating_stats"]
    assert round(rating_stats["avg"], 2) == 3.9
    assert round(rating_stats["min"], 2) == 3.0
    assert round(rating_stats["max"], 2) == 4.8


async def test_full_query_with_aggregations(es_client):
    """Тест полноценного запроса с агрегациями"""
    from es.main_query.aggregation import StatsAgg, TermsAgg
    from es.main_query.main import MainQuery
    from es.main_query.query import MultiMatch

    # Полноценный запрос с агрегациями
    full_query = (
        MainQuery()
        .query(
            MultiMatch(
                query="phone",
                fields=["product_name", "description"],
                fuzziness="AUTO",
            )
        )
        .add_agg(TermsAgg("categories", "category", size=5))
        .add_agg(TermsAgg("brands", "brand", size=5))
        .add_agg(StatsAgg("price_stats", "base_price"))
        .size(8)
        .source_filter(includes=["product_name", "description", "base_price", "rating", "brand"])
    )

    result = await es_client.aggregate(base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=full_query())

    assert len(result["hits"]["hits"]) == 2
    assert "aggregations" in result

    # Проверяем агрегации
    categories = result["aggregations"]["categories"]["buckets"]
    brands = result["aggregations"]["brands"]["buckets"]
    price_stats = result["aggregations"]["price_stats"]

    assert len(categories) > 0
    assert len(brands) > 0
    assert "avg" in price_stats


async def test_stats_query(es_client):
    """Тест запроса общей статистики"""
    from es.main_query.aggregation import CardinalityAgg, StatsAgg
    from es.main_query.main import MainQuery

    # Общая статистика
    stats_query = MainQuery(
        aggs=[
            CardinalityAgg("total_categories", "category"),
            CardinalityAgg("total_brands", "brand"),
            StatsAgg("global_stats", "base_price"),
        ],
        size=0,
        _source=False,
    )

    result = await es_client.aggregate(base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=stats_query())

    categories_count = result["aggregations"]["total_categories"]["value"]
    brands_count = result["aggregations"]["total_brands"]["value"]
    avg_price = result["aggregations"]["global_stats"]["avg"]

    assert int(categories_count) == 6  # Все категории
    assert int(brands_count) == 9  # Все бренды
    assert round(avg_price, 2) == 261.72


async def test_nested_aggregation(es_client):
    """Тест nested агрегаций"""
    from es.main_query.aggregation import FilterAgg, NestedAgg, StatsAgg, TermsAgg
    from es.main_query.main import MainQuery
    from es.main_query.query import Range

    # Nested агрегации
    nested_analysis = MainQuery(
        aggs=[
            NestedAgg(
                name="variants_in_stock",
                path="variants",
                aggs=[
                    FilterAgg(
                        name="available_variants",
                        _filter=Range(field="variants.stock", gt=0),
                        aggs=[
                            TermsAgg("colors", "variants.color", size=3),
                            StatsAgg("price_stats", "variants.price_modifier"),
                        ],
                    )
                ],
            )
        ],
        size=0,
    )

    result = await es_client.aggregate(base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=nested_analysis())

    data = result["aggregations"]["variants_in_stock"]["available_variants"]
    buckets = data["colors"]["buckets"]

    assert data["doc_count"] == 97
    assert len(buckets) == 3
    assert [(bucket["doc_count"], bucket["key"]) for bucket in buckets] == [(15, "silver"), (14, "black"), (14, "blue")]


async def test_nested_query(es_client):
    """Тест nested запросов"""
    from es.main_query.main import MainQuery
    from es.main_query.query import Bool, NestedQuery, Range

    # Nested запросы
    nested_query = MainQuery(
        query=NestedQuery(
            path="variants",
            query=Bool(_must=[Range(field="variants.stock", gt=0), Range(field="variants.price_modifier", gt=0)]),
            score_mode="none",
        ),
        size=15,
    )

    result = await es_client.search(
        base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=nested_query(), response_model=ProductShortReadSchema
    )

    assert result.total == 44
    for hit in result.sources:
        assert any(variant.stock > 0 and variant.price_modifier > 0 for variant in hit.variants)


async def test_computed_fields(es_client):
    """Тест вычисляемых полей на клиенте"""
    from es.main_query.main import MainQuery
    from es.main_query.query import Match

    query = MainQuery(
        query=Match(query="laptop", field="category"),
        size=1,
    )

    result = await es_client.search(
        base_alias=settings.ES_PRODUCTS_BASE_ALIAS, body=query(), response_model=ProductReadSchema
    )

    assert result.total == 17
    source = result.sources[0]

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
