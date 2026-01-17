"""
Документ для истории операций реиндексации.
"""

from app.config.common import settings
from elasticsearch.dsl import AsyncDocument, Date, Keyword
from es.dsl.analysis import NORMALIZER_ONLY_SETTINGS
from es.dsl.fields import RussianKeywordField


class ReindexHistoryDocument(AsyncDocument):
    """
    Запись о выполнении операции реиндекса.

    Используется для:
    - Отслеживания прогресса миграции
    - Восстановления после сбоев
    - Аудита изменений схемы данных
    """

    # Базовый алиас, для которого выполняется реиндекс
    base_alias = RussianKeywordField()
    # Аналогично:
    # base_alias = Keyword(normalizer="lowercase_normalizer")

    started_at = Date()  # Время начала операции
    source_index = Keyword()  # Исходный индекс (старая версия)
    dest_index = Keyword()  # Целевой индекс (новая версия)
    task_id = Keyword()  # Идентификатор задачи в Elasticsearch

    class Index:
        """Настройки индекса истории."""

        name = f"{settings.ES_HISTORY_BASE_ALIAS}_v1"

        settings = {
            "number_of_shards": 1,  # Один шард для логов
            "number_of_replicas": 0,  # Без реплик в тестовой среде
            "analysis": NORMALIZER_ONLY_SETTINGS,
        }
