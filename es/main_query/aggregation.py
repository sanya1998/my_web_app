from typing import Any, Dict, List, Optional

from es.main_query.query import Query


class Aggregation:
    """Базовый класс для всех агрегаций"""

    agg_type: str

    def __init__(self, name: str, aggs: Optional[List["Aggregation"]] = None, **params: Any):
        """
        Args:
            name: название агрегации
            aggs: список дочерних агрегаций (опционально)
            **params: дополнительные параметры для агрегации
        """
        self.name: str = name
        self.aggs: Optional[List["Aggregation"]] = aggs
        self.params: Dict[str, Any] = params

    @property
    def agg_value(self) -> Dict[str, Any]:
        """Возвращает значение агрегации (должен быть реализован в дочерних классах)"""
        raise NotImplementedError

    def __call__(self) -> Dict[str, Any]:
        result = {self.name: {self.agg_type: self.agg_value}}
        if self.aggs:
            result[self.name]["aggs"] = {k: v for agg in self.aggs for k, v in agg().items()}
        return result


class FieldAgg(Aggregation):
    """Базовый класс для агрегаций, работающих с конкретным полем"""

    value_key: str = "field"

    def __init__(self, name: str, field: str, **params: Any):
        self.field: str = field
        super().__init__(name, **params)

    @property
    def agg_value(self) -> Dict[str, Any]:
        return {self.value_key: self.field, **self.params}


class FilterAgg(Aggregation):
    """
    Фильтр-агрегация - применяет фильтр ко всем документам

    Параметры:
    - name: название агрегации
    - filter: запрос-фильтр для отбора документов

    Использование:
    - Подсчет документов, удовлетворяющих определенному условию
    - Вложенные агрегации внутри фильтра

    Пример:
    ```python
    FilterAgg(
        name="discounted_products",
        filter=Term(field="is_on_sale", value=True)
    )
    ```
    """

    agg_type = "filter"

    def __init__(self, name: str, _filter: Query, **params: Any):
        self.filter: Query = _filter
        super().__init__(name, **params)

    @property
    def agg_value(self) -> Dict[str, Any]:
        return {**self.filter(), **self.params}


class PipelineAgg(Aggregation):
    """Базовый класс для конвейерных агрегаций (работают с результатами других агрегаций)"""

    value_key: str = "buckets_path"

    def __init__(self, name: str, buckets_path: str, **params: Any):
        self.buckets_path: str = buckets_path
        super().__init__(name, **params)

    @property
    def agg_value(self) -> Dict[str, Any]:
        return {self.value_key: self.buckets_path, **self.params}


class GlobalAgg(Aggregation):
    """
    Глобальная агрегация - выполняется на всех документах независимо от запроса

    Параметры:
    - name: название агрегации

    Особенности:
    - Игнорирует основной поисковый запрос
    - Полезно для подсчета общих статистик по всему индексу
    - Часто используется в комбинации с другими агрегациями для сравнения
    """

    agg_type = "global"

    @property
    def agg_value(self) -> Dict[str, Any]:
        return self.params


class TermsAgg(FieldAgg):
    """
    Терм-агрегация - группировка по уникальным значениям поля

    Параметры:
    - name: название агрегации
    - field: поле для группировки

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - size: количество возвращаемых бакетов (по умолчанию 10)
    - order: сортировка бакетов ({"_count": "desc"}, {"_key": "asc"})
    - min_doc_count: минимальное количество документов в бакете
    - include: включение значений по паттерну
    - exclude: исключение значений по паттерну
    - missing: значение для документов без поля
    - show_term_doc_count_error: показывать ошибки подсчета документов
    """

    agg_type = "terms"


class RangeAgg(FieldAgg):
    """
    Агрегация по диапазонам значений

    Параметры:
    - name: название агрегации
    - field: поле для агрегации
    - ranges: список диапазонов ([{"to": 100}, {"from": 100, "to": 500}])

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - keyed: возвращать результат как словарь с ключами
    - missing: значение для документов без поля
    """

    agg_type = "range"

    def __init__(self, name: str, field: str, ranges: List[Dict[str, Any]], **params: Any):
        self.ranges: List[Dict[str, Any]] = ranges
        super().__init__(name, field, **params)

    @property
    def agg_value(self) -> Dict[str, Any]:
        return {self.value_key: self.field, "ranges": self.ranges, **self.params}


class DateHistogramAgg(FieldAgg):
    """
    Дата-гистограмма - группировка по временным интервалам

    Параметры:
    - name: название агрегации
    - field: поле с датой

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - calendar_interval: временной интервал ('day', 'week', 'month', 'quarter', 'year')
    - fixed_interval: фиксированный интервал ('1d', '2w', '30d')
    - format: формат даты для ключей бакетов
    - time_zone: временная зона
    - offset: смещение временных интервалов
    - extended_bounds: расширенные границы гистограммы
    - min_doc_count: минимальное количество документов в бакете
    - size: количество возвращаемых бакетов
    - order: сортировка бакетов
    """

    agg_type = "date_histogram"


class StatsAgg(FieldAgg):
    """
    Статистическая агрегация - базовые статистики по числовому полю

    Параметры:
    - name: название агрегации
    - field: числовое поле для анализа

    Возвращает:
    - count: количество значений
    - min: минимальное значение
    - max: максимальное значение
    - avg: среднее значение
    - sum: сумма значений

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - missing: значение для документов без поля
    - sigma: настройки для расширенной статистики
    """

    agg_type = "stats"


class CardinalityAgg(FieldAgg):
    """
    Агрегация уникальных значений - приблизительное количество уникальных элементов

    Параметры:
    - name: название агрегации
    - field: поле для подсчета уникальных значений

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - precision_threshold: контроль точности подсчета (до 40000)
    - missing: значение для документов без поля
    - rehash: пересчет хешей для точности
    """

    agg_type = "cardinality"


class ValueCountAgg(FieldAgg):
    """
    Точный подсчет значений в поле

    Параметры:
    - name: название агрегации
    - field: поле для подсчета значений

    Особенности:
    - Подсчитывает ВСЕ значения поля (включая дубликаты)
    - В отличие от CardinalityAgg, который считает только уникальные значения
    - Полезен для подсчета общего количества элементов в массиве
    """

    agg_type = "value_count"


class NestedAgg(Aggregation):
    """
    Вложенная агрегация - для работы с nested полями

    Параметры:
    - name: название агрегации
    - path: путь к nested полю
    - aggs: список дочерних агрегаций (опционально)

    Использование:
    ```python
    NestedAgg(
        name="variants_analysis",
        path="variants",
        aggs=[
            TermsAgg("colors", "variants.color", size=5),
            StatsAgg("price_stats", "variants.price_modifier")
        ]
    )
    ```
    """

    agg_type = "nested"
    value_key: str = "path"

    def __init__(self, name: str, path: str, aggs: List["Aggregation"], **params: Any):
        if not aggs:
            raise ValueError("NestedAgg requires at least one sub-aggregation")
        self.path: str = path
        super().__init__(name, aggs=aggs, **params)

    @property
    def agg_value(self) -> Dict[str, Any]:
        return {self.value_key: self.path, **self.params}


class AvgBucketAgg(PipelineAgg):
    """
    Среднее значение по бакетам другой агрегации

    Параметры:
    - name: название агрегации
    - buckets_path: путь к агрегации-источнику

    Пример использования:
    - Средняя цена товаров в каждой категории
    - Средний рейтинг в каждом ценовом диапазоне
    """

    agg_type = "avg_bucket"


class SumBucketAgg(PipelineAgg):
    """
    Сумма значений по бакетам другой агрегации

    Параметры:
    - name: название агрегации
    - buckets_path: путь к агрегации-источнику

    Пример использования:
    - Общая выручка по каждой категории товаров
    - Суммарное количество товаров в каждом диапазоне цен
    """

    agg_type = "sum_bucket"


class MaxBucketAgg(PipelineAgg):
    """
    Максимальное значение по бакетам другой агрегации

    Параметры:
    - name: название агрегации
    - buckets_path: путь к агрегации-источнику

    Пример использования:
    - Максимальная цена в каждой категории
    - Самый высокий рейтинг в каждом бренде
    """

    agg_type = "max_bucket"


class MinBucketAgg(PipelineAgg):
    """
    Минимальное значение по бакетам другой агрегации

    Параметры:
    - name: название агрегации
    - buckets_path: путь к агрегации-источнику

    Пример использования:
    - Минимальная цена в каждой категории
    - Самый низкий рейтинг в каждом ценовом диапазоне
    """

    agg_type = "min_bucket"


class StatsBucketAgg(PipelineAgg):
    """
    Статистика по значениям бакетов другой агрегации

    Параметры:
    - name: название агрегации
    - buckets_path: путь к агрегации-источнику

    Возвращает:
    - count, min, max, avg, sum по значениям бакетов

    Пример использования:
    - Статистика по ценам товаров в разных категориях
    - Анализ распределения рейтингов по брендам
    """

    agg_type = "stats_bucket"


class DerivativeAgg(PipelineAgg):
    """
    Производная (изменение) значений между соседними бакетами

    Параметры:
    - name: название агрегации
    - buckets_path: путь к агрегации-источнику

    Пример использования:
    - Изменение средней цены между ценовыми диапазонами
    - Темп роста количества товаров по месяцам
    """

    agg_type = "derivative"


class CumulativeSumAgg(PipelineAgg):
    """
    Кумулятивная сумма значений бакетов

    Параметры:
    - name: название агрегации
    - buckets_path: путь к агрегации-источнику

    Пример использования:
    - Накопительная выручка по месяцам
    - Кумулятивное количество проданных товаров по дням
    """

    agg_type = "cumulative_sum"


if __name__ == "__main__":
    print("=== ПРИМЕРЫ АГРЕГАЦИЙ (БЕЗ MainQuery) ===")

    # 1. 📊 БАЗОВАЯ АГРЕГАЦИЯ - Уникальные категории
    print("\n1. 📊 Уникальные категории товаров:")
    categories_agg = TermsAgg(name="product_categories", field="category", size=20, order={"_count": "desc"})
    print("Categories Agg:", categories_agg())

    # 2. 💰 ЦЕНОВЫЕ ДИАПАЗОНЫ
    print("\n2. 💰 Распределение по ценовым диапазонам:")
    price_ranges = [
        {"to": 100},
        {"from": 100, "to": 500},
        {"from": 500, "to": 1000},
        {"from": 1000},
    ]
    price_agg = RangeAgg(name="price_distribution", field="price", ranges=price_ranges, keyed=True)
    print("Price Ranges Agg:", price_agg())

    # 3. ⭐ СТАТИСТИКА РЕЙТИНГОВ
    print("\n3. ⭐ Статистика рейтингов:")
    stats_agg = StatsAgg("rating_stats", "rating")
    print("Stats Agg:", stats_agg())

    # 4. 🏷️ УНИКАЛЬНЫЕ БРЕНДЫ
    print("\n4. 🏷️ Уникальные бренды:")
    brands_agg = TermsAgg(name="unique_brands", field="brand", size=15, min_doc_count=2)
    print("Brands Agg:", brands_agg())

    # 5. 📅 ТОВАРЫ ПО МЕСЯЦАМ
    print("\n5. 📅 Товары по месяцам создания:")
    date_agg = DateHistogramAgg(
        name="products_by_month",
        field="created_date",
        calendar_interval="month",
        format="yyyy-MM",
    )
    print("Date Histogram Agg:", date_agg())

    # 6. 🔢 УНИКАЛЬНЫЕ ЗНАЧЕНИЯ
    print("\n6. 🔢 Уникальные бренды (Cardinality):")
    cardinality_agg = CardinalityAgg("unique_brands_count", "brand")
    print("Cardinality Agg:", cardinality_agg())

    # 7. 🔍 ФИЛЬТР-АГРЕГАЦИЯ
    print("\n7. 🔍 Товары со скидкой:")
    from es.main_query.query import Term

    filter_agg = FilterAgg(name="discounted_products", _filter=Term(field="is_on_sale", value=True))
    print("Filter Agg:", filter_agg())

    # 8. 🌍 ГЛОБАЛЬНАЯ АГРЕГАЦИЯ
    print("\n8. 🌍 Глобальная статистика:")
    global_agg = GlobalAgg("global_stats")
    print("Global Agg:", global_agg())

    print("\n9. 🏷️ Nested агрегация (анализ вариантов товаров):")

    from es.main_query.query import Range as RangeQuery

    # Анализ вариантов товаров, которые есть в наличии (stock > 0)
    # Получаем: популярные цвета и статистику по модификаторам цены для доступных вариантов
    in_stock_nested = NestedAgg(
        name="in_stock_variants",
        path="variants",
        aggs=[
            FilterAgg(
                name="available_variants",
                _filter=RangeQuery(field="variants.stock", gt=0),
                aggs=[
                    TermsAgg("available_colors", "variants.color", size=3),
                    StatsAgg("available_price_stats", "variants.price_modifier"),
                ],
            )
        ],
    )
    print("In-stock Nested Agg:", in_stock_nested())
    # "doc_count": 850,  # Всего вариантов в наличии (stock > 0)
    # "available_colors": {
    #   "buckets": [
    #     {"key": "Black", "doc_count": 250}, {"key": "White", "doc_count": 180}, {"key": "Silver", "doc_count": 120}
    #   ]
    # },
    # "available_price_stats": {
    #   "count": 850, "min": -50.0, "max": 200.0, "avg": 25.5, "sum": 21675.0
    # }

    print("\n✅ ВСЕ АГРЕГАЦИИ СОЗДАНЫ!")
