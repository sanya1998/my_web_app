from app.config.common import settings
from es.clients.base import BaseESClient
from es.main_query.aggregation import CardinalityAgg, FilterAgg, NestedAgg, RangeAgg, StatsAgg, TermsAgg
from es.main_query.main import MainQuery
from es.main_query.query import Bool, Match, MatchAll, MultiMatch, NestedQuery, Range, Term


async def search():
    """
    Тестирование всех типов запросов с реальным подключением к Elasticsearch
    """
    async with BaseESClient(settings.ES_HOSTS) as es:
        print("🔍 ТЕСТИРОВАНИЕ ЗАПРОСОВ С REAL ELASTICSEARCH")

        # 1. ПРОСТЫЕ ЗАПРОСЫ
        print("\n=== 1. ПРОСТЫЕ ЗАПРОСЫ ===")

        # Match запрос
        match_query = MainQuery(
            query=Match(query="smartphone", field="category", fuzziness="AUTO"),
            size=5,
        )
        result_match = await es.search(index=settings.ES_PRODUCTS_BASE_ALIAS, body=match_query())
        print(f"📱 Match запрос: {len(result_match['hits']['hits'])} результатов")

        # Term запрос
        term_query = MainQuery(query=Term(field="category", value="smartphone"), size=3)
        result_term = await es.search(index=settings.ES_PRODUCTS_BASE_ALIAS, body=term_query())
        print(f"🏷️ Term запрос: {len(result_term['hits']['hits'])} результатов")

        # Range запрос
        range_query = MainQuery(query=Range(field="price", gte=500, lte=1000), size=3)
        result_range = await es.search(index=settings.ES_PRODUCTS_BASE_ALIAS, body=range_query())
        print(f"💰 Range запрос: {len(result_range['hits']['hits'])} результатов")

        # 2. КОМБИНИРОВАННЫЕ ЗАПРОСЫ
        print("\n=== 2. КОМБИНИРОВАННЫЕ ЗАПРОСЫ ===")

        # С операторами
        complex_with_operators = MainQuery(
            query=(
                Match(query="phone", field="product_name")
                | MultiMatch(query="wireless", fields=["product_name", "description", "features"])
            )
            & Range(field="price", gte=300, lte=1500)
            & Term(field="is_available", value=True),
            size=10,
        )
        result_complex = await es.search(index=settings.ES_PRODUCTS_BASE_ALIAS, body=complex_with_operators())
        print(f"🎯 Комплексный запрос (операторы): {len(result_complex['hits']['hits'])} результатов")

        # Тот же запрос через Bool
        complex_with_bool = MainQuery(
            query=Bool(
                _should=[
                    Match(query="phone", field="product_name"),
                    MultiMatch(
                        query="wireless",  # В данных с большой буквы: "Wireless", но найдет благодаря нормализатору
                        fields=["product_name", "description", "features"],
                    ),
                ],
                _must=[
                    Range(field="price", gte=300, lte=1500),
                    Term(field="is_available", value=True),
                ],
                minimum_should_match=1,
            ),
            size=10,
        )
        result_bool = await es.search(index=settings.ES_PRODUCTS_BASE_ALIAS, body=complex_with_bool())
        print(f"🎯 Комплексный запрос (Bool): {len(result_bool['hits']['hits'])} результатов")

        # 3. ЗАПРОСЫ С АГРЕГАЦИЯМИ
        print("\n=== 3. ЗАПРОСЫ С АГРЕГАЦИЯМИ ===")

        # Аналитика по брендам - через aggs (список)
        brands_analysis = MainQuery(
            query=MatchAll(),
            aggs=[
                TermsAgg("top_brands", "brand", size=5),  # 👈 Только агрегация, без имени
                StatsAgg("price_stats", "price"),
            ],
            size=0,
        )
        result_brands = await es.search(index=settings.ES_PRODUCTS_BASE_ALIAS, body=brands_analysis())
        brands_buckets = result_brands["aggregations"]["top_brands"]["buckets"]
        print(f"📊 Аналитика брендов: {len(brands_buckets)} брендов")
        for bucket in brands_buckets[:3]:
            print(f"   - {bucket['key']}: {bucket['doc_count']} товаров")

        # Аналитика ценовых диапазонов - через add_agg
        price_analysis = (
            MainQuery()
            .query(Range(field="price", lte=2000))
            .add_agg(
                RangeAgg(  # 👈 Только агрегация, без имени
                    "price_ranges",
                    "price",
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
        result_prices = await es.search(index=settings.ES_PRODUCTS_BASE_ALIAS, body=price_analysis())
        price_ranges = result_prices["aggregations"]["price_ranges"]["buckets"]
        print(f"💰 Ценовые диапазоны: {len(price_ranges)} сегментов")

        # 4. ПОЛНОЦЕННЫЙ ЗАПРОС С АГРЕГАЦИЯМИ
        print("\n=== 4. ПОЛНОЦЕННЫЙ ЗАПРОС С АГРЕГАЦИЯМИ ===")

        full_query = (
            MainQuery()
            .query(
                MultiMatch(
                    query="phone",  # 👈 Упростим запрос для лучших результатов
                    fields=["product_name", "description"],
                    fuzziness="AUTO",
                )
            )
            .add_agg(TermsAgg("categories", "category", size=5))
            .add_agg(TermsAgg("brands", "brand", size=5))
            .add_agg(StatsAgg("price_stats", "price"))
            .size(8)
            .source_filter(includes=["product_name", "price", "rating", "brand"])
        )

        result_full = await es.search(index=settings.ES_PRODUCTS_BASE_ALIAS, body=full_query())

        print(f"🚀 Полноценный запрос: {len(result_full['hits']['hits'])} результатов")
        print(f"📊 Всего найдено: {result_full['hits']['total']['value']} товаров")

        # Покажем агрегации
        if "aggregations" in result_full:
            categories = result_full["aggregations"]["categories"]["buckets"]
            print(f"📈 Категории: {len(categories)} категорий найдено")
            if categories:
                print(f"   Самая популярная: {categories[0]['key']} ({categories[0]['doc_count']} товаров)")

        # 5. ОБЩАЯ СТАТИСТИКА
        print("\n=== 5. ОБЩАЯ СТАТИСТИКА ===")

        stats_query = MainQuery(
            query=MatchAll(),
            aggs=[
                CardinalityAgg("total_categories", "category"),
                CardinalityAgg("total_brands", "brand"),
                StatsAgg("global_stats", "price"),
            ],
            size=0,
            _source=False,
        )
        result_stats = await es.search(index=settings.ES_PRODUCTS_BASE_ALIAS, body=stats_query())

        categories_count = result_stats["aggregations"]["total_categories"]["value"]
        brands_count = result_stats["aggregations"]["total_brands"]["value"]
        avg_price = result_stats["aggregations"]["global_stats"]["avg"]

        print("📈 Общая статистика:")
        print(f"   Уникальных категорий: {int(categories_count)}")
        print(f"   Уникальных брендов: {int(brands_count)}")
        if avg_price is not None:
            print(f"   Средняя цена: ${avg_price:.2f}")

        # 6. NESTED АГРЕГАЦИИ
        print("\n=== 6. NESTED АГРЕГАЦИИ ===")

        nested_analysis = MainQuery(
            query=MatchAll(),
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
        result_nested = await es.search(index=settings.ES_PRODUCTS_BASE_ALIAS, body=nested_analysis())

        if "aggregations" in result_nested:
            data = result_nested["aggregations"]["variants_in_stock"]["available_variants"]
            colors = data["colors"]["buckets"]

            print(f"📦 Вариантов в наличии: {data['doc_count']}")
            print(f"🎨 Топ цвета: {', '.join(c['key'] + '(' + str(c['doc_count']) + ')' for c in colors)}")
            print(f"💰 Надбавка: ${data['price_stats']['avg']:.1f} в среднем")

        # 7. NESTED ЗАПРОСЫ
        print("\n=== 7. NESTED ЗАПРОСЫ ===")

        # Товары с вариантами в наличии и положительной надбавкой
        nested_query = MainQuery(
            query=NestedQuery(
                path="variants",
                query=Bool(_must=[Range(field="variants.stock", gt=0), Range(field="variants.price_modifier", gt=0)]),
                score_mode="none",
            ),
            size=2,
            _source=["product_name", "variants"],
        )
        result_nested = await es.search(index=settings.ES_PRODUCTS_BASE_ALIAS, body=nested_query())
        print(f"🚀 По вложенным полям запрос: {len(result_nested['hits']['hits'])} результатов")

        # В поисковых запросах
        runtime_query = MainQuery(
            query=Match(query="smartphone", field="category"),
            size=10,
            # Запрашиваем runtime fields
            runtime_mappings={
                "total_stock": {"type": "long"},
                "min_price": {"type": "double"},
                "max_price": {"type": "double"},
                "available_colors": {"type": "keyword"},
            },
        )
        result_runtime = await es.search(index=settings.ES_PRODUCTS_BASE_ALIAS, body=runtime_query())
        print(f"🚀 По runtime полям запрос: {len(result_runtime['hits']['hits'])} результатов")

        print("\n🎉 ВСЕ ЗАПРОСЫ И АГРЕГАЦИИ УСПЕШНО ВЫПОЛНЕНЫ!")


if __name__ == "__main__":
    import asyncio

    # Запускаем асинхронно
    asyncio.run(search())
