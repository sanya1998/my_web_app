from typing import List, Optional

from es.clients.models.document import OperationType
from pydantic import BaseModel


class DocumentResult(BaseModel):
    """Результат операции с документом"""

    id: str  # ID документа
    index: str  # Индекс, в котором выполнилась операция
    version: int  # Версия документа после операции
    operation: OperationType  # Тип операции
    seq_no: Optional[int] = None  # Порядковый номер изменения для OCC*
    primary_term: Optional[int] = None  # номер шарда-лидера для OCC
    # * OCC - optimistic concurrency control. Используют для условных операций:
    # "обнови, только если seq_no=5 и primary_term=1".


class SearchResult(BaseModel):
    """Унифицированная модель результатов поиска"""

    sources: List[BaseModel]  # Документы (валидированные модели)
    total: int  # Общее количество найденных
    took: int  # Время выполнения в мс
