from typing import Any, Dict, Optional

from pydantic import BaseModel


class IndexConfig(BaseModel):
    base_alias: str
    version: str
    settings: Optional[Dict[str, Any]] = None  # Если None, Elasticsearch использует дефолтные настройки
    mappings: Optional[Dict[str, Any]] = None  # Если None, создаётся индекс без маппингов (dynamic mapping)
