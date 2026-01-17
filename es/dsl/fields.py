"""
Кастомные поля Elasticsearch DSL.

Предоставляет удобные поля с предустановленными настройками анализа.
Соответствуют полям из YAML-конфигурации.
"""

from elasticsearch.dsl import Keyword, Text
from es.dsl.analysis import LOWERCASE_NORMALIZER, RUSSIAN_INDEX_ANALYZER, RUSSIAN_SEARCH_ANALYZER


class RussianTextField(Text):
    """
    Текстовое поле с русским анализом.

    Аналог searchable_text из YAML-конфигурации.
    Использует:
    - russian_index analyzer для индексации
    - russian_search analyzer для поиска
    """

    def __init__(self, **kwargs):
        super().__init__(analyzer=RUSSIAN_INDEX_ANALYZER, search_analyzer=RUSSIAN_SEARCH_ANALYZER, **kwargs)


class RussianKeywordField(Keyword):
    """
    Ключевое поле с нормализацией в нижний регистр.

    Аналог filterable_keyword из YAML-конфигурации.
    Использует lowercase_normalizer для case-insensitive сравнений.
    """

    def __init__(self, **kwargs):
        super().__init__(normalizer=LOWERCASE_NORMALIZER, **kwargs)


class RussianTextWithKeywordField(Text):
    """
    Текстовое поле с русским анализом и дополнительным keyword-полем.

    Аналог text_with_keyword из YAML-конфигурации.
    Основное поле: русский анализ для полнотекстового поиска
    Поле exact: нормализованный keyword для точного поиска
    """

    def __init__(self, **kwargs):
        # Чтобы текст использовать для точного поиска:
        fields = kwargs.pop("fields", {})
        fields["exact"] = RussianKeywordField()

        super().__init__(
            analyzer=RUSSIAN_INDEX_ANALYZER, search_analyzer=RUSSIAN_SEARCH_ANALYZER, fields=fields, **kwargs
        )
