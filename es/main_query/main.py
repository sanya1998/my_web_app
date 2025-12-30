from typing import Any, Dict, List, Optional, Union

from es.main_query.aggregation import Aggregation, CardinalityAgg, DateHistogramAgg, RangeAgg, StatsAgg, TermsAgg
from es.main_query.query import Bool, Match, Query, Range, Term


class MainQuery:
    """
    Главный поисковый запрос, готовый к отправке в Elasticsearch

    Параметры:
    - query: основной поисковый запрос
    - size: количество возвращаемых результатов (по умолчанию None = ES использует свое значение по умолчанию 10)
    - from_: смещение для пагинации (None = ES значение по умолчанию 0)
    - sort: список полей для сортировки
    - search_after: значение для поиска после курсора
    - _source: фильтрация возвращаемых полей (по умолчанию None = ES вернет все поля)
        * None - ES поведение по умолчанию (все поля)
        * True - все поля документа
        * False - отключить _source
        * List[str] - только указанные поля
        * Dict[str, Any] - сложная фильтрация
    - highlight: настройки подсветки результатов
    - aggs: агрегации для аналитики
    - explain: включить объяснение релевантности
    - timeout: таймаут выполнения запроса
    """

    def __init__(
        self,
        query: Optional[Query] = None,
        size: Optional[int] = None,
        from_: Optional[int] = None,
        sort: Optional[List[Dict[str, Any]]] = None,
        search_after: Optional[List[Any]] = None,
        _source: Optional[Union[bool, List[str], Dict[str, Any]]] = None,
        highlight: Optional[Dict[str, Any]] = None,
        aggs: Optional[List[Aggregation]] = None,
        explain: Optional[bool] = None,
        timeout: Optional[str] = None,
        **kwargs,
    ):
        self._query: Optional[Query] = query
        self._size: Optional[int] = size
        self._from: Optional[int] = from_
        self._sort: List[Dict[str, Any]] = sort or []
        self._search_after: Optional[List[Any]] = search_after
        self._source: Optional[Union[bool, List[str], Dict[str, Any]]] = _source
        self._highlight: Optional[Dict[str, Any]] = highlight
        self._aggs: List[Aggregation] = aggs or []
        self._explain: Optional[bool] = explain
        self._timeout: Optional[str] = timeout
        self._kwargs: Dict[str, Any] = kwargs

    def query(self, query: Query) -> "MainQuery":
        """Установить основной поисковый запрос"""
        self._query = query
        return self

    def size(self, size: int) -> "MainQuery":
        """Установить количество возвращаемых результатов"""
        self._size = size
        return self

    def from_(self, from_: int) -> "MainQuery":
        """Установить смещение для пагинации"""
        self._from = from_
        return self

    def paginate(self, page: int, per_page: int) -> "MainQuery":
        """Упрощенная пагинация"""
        self._from = (page - 1) * per_page
        self._size = per_page
        return self

    def sort(self, field: str, order: Optional[str] = None) -> "MainQuery":
        """Добавить поле для сортировки"""
        sort_item = {field: {"order": order}} if order else field
        self._sort.append(sort_item)
        return self

    def search_after(self, values: List[Any]) -> "MainQuery":
        """Установить значение для поиска после курсора"""
        self._search_after = values
        return self

    def source_filter(self, includes: List[str] = None, excludes: Optional[List[str]] = None) -> "MainQuery":
        """
        Фильтрация с includes/excludes

        - includes=["group_*"], excludes=["group_secret"] - все group_ поля кроме group_secret
        - includes=["user.*"], excludes=["user.password"]} - user кроме user.password
        - includes=["*"], excludes=["*.internal"]} - все кроме internal полей
        """
        source_config = {}
        if includes:
            source_config["includes"] = includes
        if excludes:
            source_config["excludes"] = excludes
        self._source = source_config if source_config else None
        return self

    def source(self, source_config: Union[bool, List[str], Dict[str, Any]]) -> "MainQuery":
        """
        Прямая передача конфигурации _source

        Возможные аргументы:
        - source_config=True - вернуть все поля документа
        - source_config=False - не возвращать поля _source (только метаданные)
        - source_config=["field_1", "field_2"] - вернуть только указанные поля
        - source_config={"includes": ["field_1"]} - вернуть только указанные поля
        - source_config={"excludes": ["field_1"]} - вернуть все КРОМЕ указанных полей
        - source_config={"includes": ["group_*"], "excludes": ["group_secret"]} - все group_ поля кроме group_secret
        - source_config={"includes": ["user.*"], "excludes": ["user.password"]} - user кроме user.password
        - source_config={"includes": ["*"], "excludes": ["*.internal"]} - все кроме internal полей
        """
        self._source = source_config
        return self

    def highlight(self, **highlight_params: Any) -> "MainQuery":
        """Настроить подсветку результатов"""
        self._highlight = highlight_params
        return self

    def aggs(self, aggregations: List[Aggregation]) -> "MainQuery":
        """
        Установить список агрегаций для аналитики

        Параметры:
        - aggregations: список объектов агрегаций

        Особенности:
        - Полностью заменяет текущий список агрегаций
        - Полезно когда нужно установить все агрегации за одну операцию
        """
        self._aggs = aggregations
        return self

    def add_agg(self, aggregation: Aggregation) -> "MainQuery":
        """
        Добавить одну агрегацию

        Параметры:
        - aggregation: объект агрегации (TermsAgg, StatsAgg, etc.)

        Особенности:
        - Добавляет агрегацию в существующий список
        - Полезно для постепенного построения запроса
        - Имя агрегации берется из самого объекта aggregation.name
        """
        self._aggs.append(aggregation)
        return self

    def explain(self, explain: bool = True) -> "MainQuery":
        """Включить объяснение релевантности"""
        self._explain = explain
        return self

    def timeout(self, timeout: str) -> "MainQuery":
        """Установить таймаут выполнения запроса"""
        self._timeout = timeout
        return self

    @staticmethod
    def add_to_dict(dictionary: Dict[str, Any], key: str, value: Any) -> None:
        """Добавить значение в словарь если оно не None"""
        if value is not None:
            dictionary[key] = value

    def __call__(self) -> Dict[str, Any]:
        """Собрать полный поисковый запрос"""
        result = self._kwargs

        # Обрабатываем агрегации
        if self._aggs:
            result["aggs"] = {}
            for agg in self._aggs:
                result["aggs"].update(agg())

        # Остальные параметры
        params_to_add = [
            ("size", self._size),
            ("from", self._from),
            ("query", self._query() if self._query else None),
            ("sort", self._sort if self._sort else None),
            ("search_after", self._search_after),
            ("_source", self._source),
            ("highlight", self._highlight),
            ("explain", self._explain),
            ("timeout", self._timeout),
        ]

        for key, value in params_to_add:
            self.add_to_dict(result, key, value)

        return result


if __name__ == "__main__":
    print("=== ОБНОВЛЕННЫЕ ПРИМЕРЫ MAINQUERY ===")

    # 1. ТОЛЬКО QUERY (без агрегаций)
    print("\n1. 📋 Простой поиск (только Query):")
    simple_search = (
        MainQuery()
        .query(Match(query="phone", field="product_name"))
        .size(10)
        .source(["product_name", "base_price", "rating"])
        .sort("base_price", "asc")
    )
    print("Результат:", simple_search())

    # 2. ТОЛЬКО АГРЕГАЦИИ (без Query) - через add_agg
    print("\n2. 📊 Только аналитика (add_agg):")
    analytics_only = (
        MainQuery()
        .add_agg(TermsAgg("categories", "category", size=5))
        .add_agg(StatsAgg("price_stats", "base_price"))
        .size(0)
    )
    print("Результат:", analytics_only())

    # 3. QUERY + АГРЕГАЦИИ - через aggs (все сразу)
    print("\n3. 🚀 Полный анализ (aggs - все сразу):")
    full_analysis_aggs = (
        MainQuery()
        .query(
            Bool(
                _must=[
                    Match(query="smartphone", field="category"),
                    Range(field="rating", gte=4.0),
                ]
            )
        )
        .aggs(
            [
                TermsAgg("brands", "brand", size=5),
                StatsAgg("price_analysis", "base_price"),
                RangeAgg("price_ranges", "base_price", [{"to": 500}, {"from": 500, "to": 1000}]),
            ]
        )
        .size(5)
    )
    print("Результат:", full_analysis_aggs())

    # 4. QUERY + АГРЕГАЦИИ - через add_agg (постепенно)
    print("\n4. 🔧 Полный анализ (add_agg - постепенно):")
    full_analysis_add = (
        MainQuery()
        .query(Match(query="laptop", field="category"))
        .add_agg(TermsAgg("top_brands", "brand", size=3))
        .add_agg(StatsAgg("rating_stats", "rating"))
        .add_agg(DateHistogramAgg("monthly", "created_date", calendar_interval="month"))
        .size(8)
        .source_filter(includes=["product_name", "brand", "base_price"])
    )
    print("Результат:", full_analysis_add())

    # 5. КОМБИНИРОВАННЫЙ ПОДХОД
    print("\n5. 🎯 Комбинированный подход:")
    combined = (
        MainQuery()
        .query(Range(field="base_price", lte=1000))
        .aggs(
            [  # Базовые агрегации
                TermsAgg("categories", "category"),
                StatsAgg("price_stats", "base_price"),
            ]
        )
        .add_agg(CardinalityAgg("unique_brands", "brand"))  # Дополнительная агрегация
        .size(0)
    )
    print("Результат:", combined())

    # 6. ЧЕРЕЗ КОНСТРУКТОР
    print("\n6. 🏗️ Через конструктор:")
    constructor_query = MainQuery(
        query=Bool(
            _must=[
                Match(query="wireless", field="features"),
                Term(field="is_available", value=True),
            ]
        ),
        aggs=[
            TermsAgg("feature_categories", "category", size=5),
            StatsAgg("availability_stats", "rating"),
        ],
        size=5,
        _source=["product_name", "base_price", "features"],
    )
    print("Результат:", constructor_query())

    print("\n🎉 ВСЕ ПРИМЕРЫ ОБНОВЛЕНЫ!")
