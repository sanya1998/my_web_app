from typing import List

from pydantic_settings import BaseSettings


class ElasticsearchSettings(BaseSettings):
    """
    Конфигурация Elasticsearch
    """

    ES_VERSION: str
    ES_HOSTS: List[str] = ["http://0.0.0.0:9200/"]
    ES_PRODUCTS_BASE_ALIAS: str = "products"
    ES_HISTORY_BASE_ALIAS: str = "reindex_history"
    ES_PASSWORD: str

    ES_INDICES_DIRECTORY: str = "es/indices"
    ES_INDEX_FILE_EXTENSION: str = "yaml"
    ES_INDEX_FILE_ENCODING: str = "utf-8"
