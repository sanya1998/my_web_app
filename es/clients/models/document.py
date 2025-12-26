from enum import Enum


class OperationType(str, Enum):
    """Типы операций с документами"""

    INDEX = "index"  # Создать или заменить (upsert)
    CREATE = "create"  # Только создать (ошибка если существует)
    UPDATE = "update"  # Обновить существующий
    DELETE = "delete"  # Удалить


class QueryOperationType(str, Enum):
    """Типы операций по запросу"""

    UPDATE_BY_QUERY = "update_by_query"
    DELETE_BY_QUERY = "delete_by_query"
