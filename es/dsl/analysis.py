"""
Настройки анализа для Elasticsearch.

Универсальная система создания настроек анализа.
"""

from typing import Dict, List

from elasticsearch.dsl import analyzer, normalizer, token_filter


# ===== УНИВЕРСАЛЬНАЯ ФУНКЦИЯ =====
def create_analysis_settings(
    normalizers: List[normalizer] = None,
    filters: List[token_filter] = None,
    analyzers: List[analyzer] = None,
) -> Dict[str, Dict]:
    """
    Создает настройки анализа из объектов elasticsearch.dsl.

    Args:
        normalizers: Список объектов normalizer
        filters: Список объектов token_filter
        analyzers: Список объектов analyzer

    Returns:
        Словарь с настройками анализа для Elasticsearch

    Пример:
        settings = create_analysis_settings(
            normalizers=[lowercase_normalizer],
            filters=[russian_stop, russian_stemmer],
            analyzers=[russian_index, russian_search]
        )
    """
    analysis_settings = {}

    # Добавляем нормализаторы
    if normalizers:
        analysis_settings["normalizer"] = {norm._name: norm.get_definition() for norm in normalizers}

    # Добавляем фильтры
    if filters:
        analysis_settings["filter"] = {flt._name: flt.get_definition() for flt in filters}

    # Добавляем анализаторы
    if analyzers:
        analysis_settings["analyzer"] = {anlz._name: anlz.get_definition() for anlz in analyzers}

    return analysis_settings


# ===== БАЗОВЫЕ ОБЪЕКТЫ ДЛЯ РУССКОГО ЯЗЫКА =====
# Константы
RUSSIAN_STOP_FILTER = "russian_stop"
RUSSIAN_STEMMER_FILTER = "russian_stemmer"
RUSSIAN_INDEX_ANALYZER = "russian_index"
RUSSIAN_SEARCH_ANALYZER = "russian_search"
LOWERCASE_NORMALIZER = "lowercase_normalizer"

# Объекты фильтров
russian_stop = token_filter(RUSSIAN_STOP_FILTER, "stop", stopwords="_russian_")
russian_stemmer = token_filter(RUSSIAN_STEMMER_FILTER, "stemmer", language="russian")

# Объект нормализатора
lowercase_normalizer = normalizer(LOWERCASE_NORMALIZER, "custom", filter=["lowercase"])

# Объекты анализаторов
russian_index = analyzer(
    RUSSIAN_INDEX_ANALYZER, "custom", tokenizer="standard", filter=["lowercase", RUSSIAN_STOP_FILTER]
)

russian_search = analyzer(
    RUSSIAN_SEARCH_ANALYZER,
    "custom",
    tokenizer="standard",
    filter=["lowercase", RUSSIAN_STOP_FILTER, RUSSIAN_STEMMER_FILTER],
)

# ===== ПРЕДОПРЕДЕЛЕННЫЕ КОНФИГУРАЦИИ =====
# Базовая русская конфигурация
RUSSIAN_ANALYSIS_SETTINGS = create_analysis_settings(
    normalizers=[lowercase_normalizer],
    filters=[russian_stop, russian_stemmer],
    analyzers=[russian_index, russian_search],
)

NORMALIZER_ONLY_SETTINGS = create_analysis_settings(normalizers=[lowercase_normalizer])
