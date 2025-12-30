# TODO: смотри elasticsearch.dsl.query. Возможно, там уже все это есть. Но желательно сохранить отсюда документацию (ru)
from typing import Any, Dict, List, Optional


class Query:
    """Базовый класс для всех запросов"""

    query_type: str

    @property
    def query_value(self) -> Any:
        raise NotImplementedError

    def __init__(self, **query_params: Any):
        self.query_params: Dict[str, Any] = query_params

    def __call__(self) -> Dict[str, Any]:
        return {self.query_type: self.query_value}

    def __and__(self, other: "Query") -> "Bool":
        return Bool(_must=[self, other])

    def __invert__(self) -> "Bool":
        return Bool(_must_not=[self])

    def __or__(self, other: "Query") -> "Bool":
        return Bool(_should=[self, other], minimum_should_match=1)

    @classmethod
    def add_to_dict(cls, dictionary: Dict[str, Any], key: str, value: Any) -> None:
        if value is not None:
            dictionary[key] = value


class MatchAll(Query):
    """Запрос для получения всех документов"""

    query_type = "match_all"

    @property
    def query_value(self) -> Dict[str, Any]:
        return self.query_params


class FuzzySearch(Query):
    """Базовый класс для нечеткого поиска (текстовый поиск с анализом)"""

    def __init__(self, query: Any, **params: Any):
        self.query: Any = query
        super().__init__(**params)


class SingleFuzzy(FuzzySearch):
    """Нечеткий поиск по одному полю"""

    def __init__(self, query: Any, field: str, **params: Any):
        self.field: str = field
        super().__init__(query, **params)

    @property
    def query_value(self) -> Dict[str, Any]:
        return {self.field: {"query": self.query, **self.query_params}}


class Match(SingleFuzzy):
    """
    Текстовый поиск с анализом

    Параметры:
    - query: поисковый запрос
    - field: поле для поиска

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - boost: усиление релевантности
    - fuzziness: допуск опечаток ('AUTO', 0, 1, 2)
    - operator: логический оператор ('and', 'or')
    - analyzer: анализатор текста
    - auto_generate_synonyms_phrase_query: генерация синонимов
    - fuzzy_transpositions: транспозиции при нечетком поиске
    - lenient: игнорировать ошибки формата
    - max_expansions: максимальное расширение префикса
    - minimum_should_match: минимальное совпадение should условий
    - prefix_length: длина префикса для нечеткого поиска
    - zero_terms_query: поведение при нулевых результатах ('none', 'all')
    """

    query_type = "match"


class MatchPhrase(SingleFuzzy):
    """
    Поиск точной фразы (с учетом порядка слов)

    Параметры:
    - query: точная фраза для поиска
    - field: поле для поиска

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - boost: усиление релевантности
    - analyzer: анализатор текста
    - slop: допуск на расстояние между словами (0 = точное совпадение)
    """

    query_type = "match_phrase"


class MultiFuzzy(FuzzySearch):
    """Нечеткий поиск по нескольким полям"""

    def __init__(self, query: str, fields: List[str], **params: Any):
        self.fields: List[str] = fields
        super().__init__(query, **params)

    @property
    def query_value(self) -> Dict[str, Any]:
        return {"query": self.query, "fields": self.fields, **self.query_params}


class MultiMatch(MultiFuzzy):
    """
    Поиск по нескольким полям

    Параметры:
    - query: поисковый запрос
    - fields: список полей для поиска

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - boost: усиление релевантности
    - type: тип поиска ('best_fields', 'most_fields', 'cross_fields', 'phrase', 'phrase_prefix')
    - tie_breaker: коэффициент связи между полями (0.0 - 1.0)
    - analyzer: анализатор текста
    - operator: логический оператор ('and', 'or')
    - minimum_should_match: минимальное совпадение should условий
    - fuzziness: допуск опечаток
    """

    query_type = "multi_match"


class QueryString(MultiFuzzy):
    """
    Расширенный поиск с синтаксисом запросов

    Параметры:
    - query: строка запроса с синтаксисом Elasticsearch
    - fields: список полей для поиска

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - boost: усиление релевантности
    - default_operator: оператор по умолчанию ('AND', 'OR')
    - analyze_wildcard: анализ wildcard-символов
    - lenient: игнорировать ошибки формата
    - fuzzy_max_expansions: максимальное расширение для нечеткого поиска
    - fuzzy_prefix_length: длина префикса для нечеткого поиска
    """

    query_type = "query_string"


class SimpleQueryString(MultiFuzzy):
    """
    Упрощенный поиск с синтаксисом запросов (более безопасный)

    Параметры:
    - query: упрощенная строка запроса
    - fields: список полей для поиска

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - boost: усиление релевантности
    - default_operator: оператор по умолчанию ('AND', 'OR')
    - analyze_wildcard: анализ wildcard-символов
    - flags: разрешенные операторы (например, 'AND|OR|PREFIX')
    """

    query_type = "simple_query_string"


class ExactSearch(Query):
    """Базовый класс для точного поиска (фильтрация по точным значениям)"""

    def __init__(self, field: str, **params: Any):
        self.field: str = field
        super().__init__(**params)


class Term(ExactSearch):
    """
    Точный поиск по значению

    Параметры:
    - field: поле для поиска
    - value: точное значение для поиска

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - boost: усиление релевантности
    - case_insensitive: регистронезависимый поиск
    """

    query_type = "term"

    def __init__(self, field: str, value: Any, **params: Any):
        self.value: Any = value
        super().__init__(field, **params)

    @property
    def query_value(self) -> Dict[str, Any]:
        return {self.field: self.value, **self.query_params}


class Terms(ExactSearch):
    """
    Точный поиск по списку значений

    Параметры:
    - field: поле для поиска
    - values: список значений для поиска

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - boost: усиление релевантности
    """

    query_type = "terms"

    def __init__(self, field: str, values: List[Any], **params: Any):
        self.values: List[Any] = values
        super().__init__(field, **params)

    @property
    def query_value(self) -> Dict[str, Any]:
        return {self.field: self.values, **self.query_params}


class Range(ExactSearch):
    """
    Поиск в диапазоне

    Параметры:
    - field: поле для поиска

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - boost: усиление релевантности
    - gte: больше или равно (greater than or equal)
    - gt: больше (greater than)
    - lte: меньше или равно (less than or equal)
    - lt: меньше (less than)
    - format: формат для дат
    - time_zone: временная зона
    - relation: отношение к диапазону ('WITHIN', 'CONTAINS', 'INTERSECTS')
    """

    query_type = "range"

    @property
    def query_value(self) -> Dict[str, Any]:
        return {self.field: self.query_params}


class Exists(ExactSearch):
    """
    Проверка существования поля

    Параметры:
    - field: поле для проверки
    """

    query_type = "exists"

    @property
    def query_value(self) -> Dict[str, Any]:
        return {"field": self.field, **self.query_params}


class NestedQuery(Query):
    """
    Запрос для поиска внутри nested объектов

    Параметры:
    - path: путь к nested полю
    - query: запрос для выполнения внутри nested

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - score_mode: как считать релевантность ('avg', 'sum', 'max', 'min', 'none')
    - ignore_unmapped: игнорировать если поле не mapped
    - inner_hits: возвращать внутренние хиты

    Пример:
    ```python
    # Найти товары с вариантом цвета "Black"
    NestedQuery(
        path="variants",
        query=Term(field="variants.color", value="Black"),
        score_mode="sum"
    )
    ```
    """

    query_type = "nested"

    def __init__(self, path: str, query: Query, **params: Any):
        self.path: str = path
        self.query: Query = query
        super().__init__(**params)

    @property
    def query_value(self) -> Dict[str, Any]:
        return {"path": self.path, "query": self.query(), **self.query_params}


class Clause(Query):
    """Базовый класс для логических условий"""

    def __init__(self, conditions: List[Query], **params: Any):
        self.conditions: List[Query] = conditions
        super().__init__(**params)

    @property
    def query_value(self) -> List[Dict[str, Any]]:
        return [q() for q in self.conditions]


class Must(Clause):
    """Обязательные условия"""

    query_type = "must"


class Filter(Clause):
    """Фильтры (без влияния на релевантность)"""

    query_type = "filter"


class MustNot(Clause):
    """Запрещенные условия"""

    query_type = "must_not"


class Should(Clause):
    """
    Желательные условия

    Параметры:
    - conditions: список условий

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - minimum_should_match: минимальное количество should условий
    """

    query_type = "should"


class Bool(Query):
    """
    Полноценный булев запрос

    Параметры:
    - _must: список обязательных условий
    - _must_not: список запрещенных условий
    - _should: список желательных условий
    - _filter: список условий-фильтров

    Другие поддерживаемые параметры Elasticsearch (через **params):
    - boost: усиление релевантности
    - minimum_should_match: минимальное количество should условий
    """

    query_type = "bool"

    def __init__(
        self,
        _must: Optional[List[Query]] = None,
        _must_not: Optional[List[Query]] = None,
        _should: Optional[List[Query]] = None,
        _filter: Optional[List[Query]] = None,
        **params: Any,
    ):
        self._must: List[Query] = _must or []
        self._must_not: List[Query] = _must_not or []
        self._should: List[Query] = _should or []
        self._filter: List[Query] = _filter or []
        super().__init__(**params)

    @property
    def query_value(self) -> Dict[str, Any]:
        return {
            **Must(self._must)(),
            **MustNot(self._must_not)(),
            **Should(self._should)(),
            **Filter(self._filter)(),
            **self.query_params,
        }


if __name__ == "__main__":
    # TODO: Взять за основу этот файл и написать тесты
    # ПРОСТЫЕ ПРИМЕРЫ - все листовые классы
    print("\n=== ПРОСТЫЕ ПРИМЕРЫ ===")

    # MatchAll
    match_all_1 = MatchAll()
    match_all_2 = MatchAll(boost=2)

    # FuzzySearch
    match_query = Match(query="smartphone", field="title", fuzziness="AUTO")
    match_phrase = MatchPhrase(query="wireless charging", field="description")
    multi_match = MultiMatch(query="fast", fields=["title", "description"])
    query_string = QueryString(query="Apple OR Samsung", fields=["brand"])
    simple_query = SimpleQueryString(query="5G", fields=["features"])

    # ExactSearch
    term_query = Term(field="category", value="electronics")
    terms_query = Terms(field="brand", values=["Apple", "Samsung"])
    range_query = Range(field="base_price", gte=500, lte=1500)
    exists_query = Exists(field="in_stock")

    print(match_all_1())
    print(match_all_2())
    print("Match:", match_query())
    print("MatchPhrase:", match_phrase())
    print("MultiMatch:", multi_match())
    print("QueryString:", query_string())
    print("SimpleQueryString:", simple_query())
    print("Term:", term_query())
    print("Terms:", terms_query())
    print("Range:", range_query())
    print("Exists:", exists_query())

    # КОМБИНИРОВАННЫЕ ПРИМЕРЫ - два представления
    print("\n=== КОМБИНИРОВАННЫЙ ЗАПРОС ===")

    # С операторами И/ИЛИ/НЕ
    with_operators = (
        (Match(query="phone", field="title") | MultiMatch(query="smart", fields=["title", "description"]))
        & ~Exists(field="discontinued")
        & Range(field="rating", gte=4.0)
    )

    # Тот же запрос без операторов
    without_operators = Bool(
        _should=[
            Match(query="phone", field="title"),
            MultiMatch(query="smart", fields=["title", "description"]),
        ],
        _must=[Range(field="rating", gte=4.0)],
        _must_not=[Exists(field="discontinued")],
        minimum_should_match=1,
    )

    print("С операторами И/ИЛИ/НЕ:")
    print(with_operators())
    print("\nТот же запрос через Bool:")
    print(without_operators())
