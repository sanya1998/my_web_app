import re
from functools import wraps
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, TypeVar, cast

from elastic_transport import ConnectionTimeout
from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ApiError, ConnectionError, NotFoundError, TransportError
from es.clients.models.document import OperationType, QueryOperationType
from es.constants import ID_FIELD_DEFAULT, WRITE_SUFFIX

F = TypeVar("F", bound=Callable[..., Any])


class BaseESClient(AsyncElasticsearch):
    """
    Базовый клиент для работы с Elasticsearch (только Dict)

    Особенности:
    - Работа только со словарями (Dict[str, Any])
    - Возвращает сырые ответы от Elasticsearch
    - Дефолтный индекс + переопределение в методах
    - Поддержка read/write алиасов
    """

    # === МАППИНГИ === # TODO: подумать, нет ли избыточности
    # Маппинг типов операций на конфигурации для одиночных операций.
    _SINGLE_OPERATION_CONFIGS: Dict[OperationType, Callable] = {
        OperationType.CREATE: lambda es, doc_data: (es.create, doc_data),
        OperationType.INDEX: lambda es, doc_data: (es.index, doc_data),
        OperationType.UPDATE: lambda es, doc_data: (es.update, {"doc": doc_data}),
        OperationType.DELETE: lambda es, _: (es.delete, None),
    }

    # Маппинг типов операций на функции-строители для массовых операций.
    _BULK_OPERATION_BUILDERS: Dict[OperationType, Callable] = {
        OperationType.INDEX: lambda operation, doc_data: [{OperationType.INDEX.value: operation}, doc_data],
        OperationType.CREATE: lambda operation, doc_data: [{OperationType.CREATE.value: operation}, doc_data],
        OperationType.UPDATE: lambda operation, doc_data: [{OperationType.UPDATE.value: operation}, {"doc": doc_data}],
        OperationType.DELETE: lambda operation, _: [{OperationType.DELETE.value: operation}],
    }

    # Маппинг типов операций по запросу на методы AsyncElasticsearch.
    _QUERY_OPERATION_METHODS: Dict[QueryOperationType, Callable] = {
        QueryOperationType.UPDATE_BY_QUERY: lambda es: es.update_by_query,
        QueryOperationType.DELETE_BY_QUERY: lambda es: es.delete_by_query,
    }

    # Константы для обёртки методов
    _INDICES_METHODS_TO_WRAP = [
        "exists",
        "create",
        "update_aliases",
        "get_alias",
        "refresh",
        "delete",
        "put_mapping",
        "get_mapping",
        "put_settings",
        "get_settings",
        "stats",
        "validate_query",
    ]

    _CLIENT_METHODS_TO_WRAP = [
        "get",
        "search",
        "count",
        "create",
        "index",
        "update",
        "delete",
        "bulk",
        "update_by_query",
        "delete_by_query",
        "reindex",
        "mget",
        "scroll",
    ]

    # === ИНИЦИАЛИЗАЦИЯ ===
    def __init__(
        self,
        hosts: Optional[List[str]] = None,
        base_alias: Optional[str] = None,
        use_write_alias: bool = False,
        **kwargs,
    ):
        """
        Инициализация клиента Elasticsearch

        Args:
            hosts: Список URL нод Elasticsearch (например: ["http://localhost:9200"])
            base_alias: Дефолтный алиас для операций (можно переопределять в методах)
            use_write_alias: Использовать _write алиас
            **kwargs: Дополнительные параметры для AsyncElasticsearch

        Примеры использования:
        ```python
        # Базовый вариант
        es = BaseESClient(hosts=["http://localhost:9200"])

        # Продвинутые настройки
        es = BaseESClient(
            hosts=settings.ELASTIC_URLS,
            default_alias="products",

            # Аутентификация
            http_auth=("user", "password"),          # HTTP базовая аутентификация
            basic_auth=("user", "password"),         # Альтернатива http_auth
            api_key=("id", "api_key"),               # API Key аутентификация

            # Настройки подключения и таймауты
            timeout=30,                              # Таймаут операций в секундах
            retry_on_timeout=True,                   # Повторять при таймауте
            max_retries=3,                           # Максимум повторов

            # Пул соединений
            maxsize=25,                              # Максимум соединений в пуле

            # Сериализация
            serializer=JSONSerializer(),             # Кастомный сериализатор

            # DNS и SSL
            use_dns_cache=True,                      # Кешировать DNS запросы
            verify_certs=False,                      # Проверять SSL сертификаты
            ssl_show_warn=False,                     # Показывать SSL предупреждения

            # Sniffing (автообнаружение узлов)
            sniff_on_start=True,                     # Обнаружить узлы при старте
            sniff_on_connection_fail=True,           # Обнаружить при ошибке соединения
            sniffer_timeout=60,                      # Таймаут для sniffing

            # Другие настройки
            request_timeout=30,                      # Таймаут HTTP запросов
            max_retries=3,                           # Максимум повторов запроса
            retry_on_status=(502, 503, 504),         # Статусы для повтора
        )
        ```
        """
        super().__init__(hosts, **kwargs)
        self._base_alias = base_alias
        self._use_write_alias = use_write_alias
        self._wrap_methods(self, self._CLIENT_METHODS_TO_WRAP)
        self._wrap_methods(self.indices, self._INDICES_METHODS_TO_WRAP)

    # === ДЕКОРАТОР-ОБРАБОТЧИК ОШИБОК ===
    @staticmethod
    def _handle_es_errors(func: F) -> F:
        """
        Декоратор для обработки ошибок Elasticsearch.

        Иерархия исключений elasticsearch-py (объединённая):

        1. ОШИБКИ ТРАНСПОРТА/СЕТИ (низкоуровневые):
           TransportError (из elastic-transport)
           ├── SniffingError (ошибка при обнаружении нод)
           ├── SerializationError (ошибка сериализации)
           ├── ConnectionError (проблемы подключения)
           │   └── TlsError (ошибка SSL/TLS)
           └── ConnectionTimeout (таймаут соединения)

        2. ОШИБКИ API ELASTICSEARCH (основные для логики приложения):
           ApiError (базовый класс для HTTP ошибок)
           ├── NotFoundError (HTTP 404 - документ/индекс не найден)
           ├── ConflictError (HTTP 409 - конфликт версий)
           ├── BadRequestError (HTTP 400 - некорректный запрос)
           ├── AuthorizationException (HTTP 403 - нет прав)
           └── AuthenticationException (HTTP 401 - ошибка аутентификации)

        3. ОБЪЕДИНЯЮЩИЙ КЛАСС (для обратной совместимости):
           ElasticsearchException (в старых версиях)

        ВАЖНЫЕ МОМЕНТЫ:
        • Таймаут ЗАПРОСА (не соединения) приходит как ApiError.
          Признаки таймаута в body ошибки:
          - "timed_out": true (для search запросов)
          - "caused_by.type": "timeout_exception" (для других операций)
        • ConnectionTimeout - это только таймаут установки TCP-соединения.
        • Все HTTP ошибки (4xx, 5xx) являются подклассами ApiError.
        """

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except ConnectionError as e:
                print(f"ES ConnectionError in {func.__name__}: {e}")
                raise
            except ConnectionTimeout as e:
                print(f"ES ConnectionTimeout in {func.__name__}: {e}")
                raise TimeoutError(f"ES connection timeout: {func.__name__}") from e
            except ApiError as e:
                if e.body and isinstance(e.body, dict):
                    is_search_timeout = e.body.get("timed_out") is True
                    if is_search_timeout:
                        print(f"ES Query Timeout in {func.__name__}: {e}")
                        raise TimeoutError(f"ES query timeout: {func.__name__}") from e
                print(f"ES API Error in {func.__name__}: {e}")
                raise
            except TransportError as e:
                print(f"ES TransportError in {func.__name__}: {e}")
                raise
            except Exception as e:
                print(f"ES Error in {func.__name__}: {e}")
                raise

        return cast(F, wrapper)

    def _wrap_method(self, original_method):
        """Обернуть метод декоратором обработки ошибок"""

        @wraps(original_method)
        @self._handle_es_errors
        async def wrapper(*args, **kwargs):
            return await original_method(*args, **kwargs)

        return wrapper

    def _wrap_methods(self, obj, method_names):
        for method_name in method_names:
            if hasattr(obj, method_name):
                original = getattr(obj, method_name)
                wrapped = self._wrap_method(original)
                setattr(obj, method_name, wrapped)

    # === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===
    @staticmethod
    def _get_write_alias(base_alias: str) -> str:
        """Получить write алиас для базового алиаса"""
        return f"{base_alias}{WRITE_SUFFIX}"

    def _resolve_alias(
        self,
        base_alias: Optional[str] = None,
    ) -> str:
        """
        Разрешение индекса с поддержкой алиасов

        Args:
            base_alias: Базовый алиас (если None, то будет использоваться дефолтный)

        Returns:
            Полное имя алиаса

        Raises:
            ValueError: если не указан базовый алиас и нет дефолтного
        """

        using_alias = base_alias or self._base_alias
        if not using_alias:
            raise ValueError("Alias must be specified either in method or in client initialization")

        if self._use_write_alias:
            return self._get_write_alias(using_alias)

        return using_alias

    async def get_indices_by_alias(self, alias: str) -> List[str] | None:
        """
        Найти индексы по базовому алиасу
        """
        try:
            response = await self.indices.get_alias(name=alias)
            indices = list(response.keys())
        except NotFoundError:
            indices = []
        return indices

    @staticmethod
    def _extract_document_data_and_id(document: Dict[str, Any], id_field: str = ID_FIELD_DEFAULT) -> Optional[str]:
        """Извлечь данные документа и ID"""
        doc_id = document.get(id_field)
        doc_id = str(doc_id) if doc_id else None
        return doc_id

    @staticmethod
    def _map_to_es_kwargs(
        doc_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Преобразовать внутренние имена параметров в имена Elasticsearch API

        Преобразования:
        - doc_id → id (потому что 'id' зарезервировано в Python)

        Все остальные параметры передаются без изменений.

        Args:
            doc_id: ID документа для операций Elasticsearch
            **kwargs: Прочие параметры для передачи в Elasticsearch API

        Returns:
            Словарь параметров, готовый для передачи в методы Elasticsearch

        Пример:
            ```python
            kwargs = self._map_to_es_kwargs(
                doc_id="123",
                refresh="wait_for",
                timeout="30s"
            )
            # kwargs = {"id": "123", "refresh": "wait_for", "timeout": "30s"}
            ```
        """
        es_kwargs = kwargs.copy()

        if doc_id:
            es_kwargs["id"] = doc_id

        return es_kwargs

    async def _single_execute(
        self,
        document: Dict[str, Any],
        operation_type: OperationType,
        base_alias: Optional[str] = None,
        id_field: str = ID_FIELD_DEFAULT,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Общий метод для одиночных операций с документами

        Args:
            document: Документ (dict)
            operation_type: Тип операции
            base_alias: Алиас (если None - дефолтный)
            id_field: Поле документа, содержащее ID
            **kwargs: Дополнительные параметры для Elasticsearch:
                - refresh: RefreshType - когда сделать изменения видимыми
                          "true" (немедленно), "false" (никогда), "wait_for" (дождаться)
                - timeout: str - таймаут операции (например: "30s", "1m", "500ms")
                - version: int - версия для optimistic concurrency control
                - if_seq_no: int - номер последовательности
                - if_primary_term: int - primary term
                - routing: str - routing ключ
                - И другие параметры соответствующих операций ES

        Returns:
            Сырой ответ ES

        Пример:
            ```python
            # Создание документа с кастомными параметрами
            await es._single_execute(
                document={"id": "123", "name": "Product"},
                operation_type=OperationType.CREATE,
                base_alias="products",
                refresh="wait_for",
                timeout="30s",
                version=5,
                routing="user_123"
            )
            ```
        """
        resolved_alias = self._resolve_alias(base_alias)
        doc_id = self._extract_document_data_and_id(document, id_field)

        config_func = self._SINGLE_OPERATION_CONFIGS[operation_type]
        es_method, body = config_func(super(), document)

        operation_kwargs = self._map_to_es_kwargs(doc_id=doc_id, **kwargs)
        result = await es_method(index=resolved_alias, body=body, **operation_kwargs)
        return result

    async def _bulk_execute(
        self,
        documents: List[Dict[str, Any]],
        operation_type: OperationType,
        base_alias: Optional[str] = None,
        id_field: str | None = ID_FIELD_DEFAULT,
        raise_on_error: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Общий метод для массовых операций (bulk index, create, update, delete)

        Args:
            documents: Список документов для обработки
            operation_type: Тип операции
            base_alias: Алиас (если None - дефолтный)
            id_field: Поле документа, содержащее ID (по умолчанию: "id").
                     Если None - Elasticsearch сгенерирует ID автоматически.
            raise_on_error: Бросать исключение при ошибках в bulk операции.
                           Если False - возвращаются результаты с ошибками.
            **kwargs: Дополнительные параметры Elasticsearch bulk API:
                - refresh: RefreshType - когда сделать изменения видимыми
                          "true" - немедленно, "false" - никогда, "wait_for" - дождаться
                - timeout: str - таймаут операции ("30s", "1m", "500ms")
                - pipeline: str - pipeline для обработки документов
                - require_alias: bool - требовать, чтобы индекс был алиасом
                - wait_for_active_shards: str | int - ждать активных шардов
                - _source: bool | str | List[str] - возвращать ли исходные документы
                - _source_excludes: List[str] - исключить поля из _source
                - _source_includes: List[str] - включить только указанные поля

                И другие параметры Elasticsearch bulk API.

        Returns:
            Сырой ответ ES

        Пример:
            ```python
            # Массовая индексация с кастомным полем ID и проверкой ошибок
            await es._bulk_execute(
                documents=products,
                operation_type=OperationType.INDEX,
                index="products",
                id_field="sku",  # Используем поле "sku" как ID
                raise_on_error=True,  # Бросать исключение при ошибках
                refresh="wait_for",
                timeout="2m",
                pipeline="product_processor"
            )
            ```
        """
        resolved_alias = self._resolve_alias(base_alias)

        operation_builder = self._BULK_OPERATION_BUILDERS[operation_type]

        operations = []

        for document in documents:
            doc_id = self._extract_document_data_and_id(document, id_field)
            operation = {"_id": doc_id} if doc_id else {}
            doc_operations = operation_builder(operation, document)
            operations.extend(doc_operations)

        result = await super().bulk(index=resolved_alias, operations=operations, **kwargs)

        # Проверка ошибок (если raise_on_error=True)
        if raise_on_error and result.get("errors"):
            failed_ids = [
                item.get(operation_type.value, {}).get("_id", "unknown")
                for item in result["items"]
                if "error" in item.get(operation_type.value, {})
            ]
            error_msg = f"Bulk {operation_type.value} failed for {len(failed_ids)} documents"
            if ids_sample := ", ".join(failed_ids):
                error_msg += f" (sample IDs: {ids_sample})"
            raise RuntimeError(error_msg)

        return result

    async def _by_query_execute(
        self,
        query: Mapping[str, Any],
        operation_type: QueryOperationType,
        base_alias: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Общий метод для операций по запросу (update_by_query, delete_by_query)

        Args:
            query: Query dict для фильтрации документов. Должен быть результатом вызова Query объекта:
            operation_type: Тип операции
            base_alias: Алиас (если None - дефолтный)
            **kwargs: Дополнительные параметры для Elasticsearch API.
                 Декоратор @_rewrite_parameters в библиотеке elasticsearch-py
                 автоматически переместит параметры из body_fields в тело запроса:

                 В body (через декоратор):
                 - query: Dict[str, Any] - уже передаётся отдельно
                 - script: Dict[str, Any] - Painless script (только для update_by_query)
                 - conflicts: str - как обрабатывать конфликты ("abort", "proceed")
                 - max_docs: int - максимальное количество документов для обработки
                 - slice: Dict[str, Any] - настройки срезов

                 Как query-параметры (остаются в kwargs):
                 - refresh: RefreshQueryType - когда сделать изменения видимыми
                 - timeout: str - таймаут операции ("30s", "1m", "500ms")
                 - wait_for_completion: bool - ждать завершения (для асинхронных операций)
                 - slices: int | str - количество срезов для параллельной обработки
                 - и другие параметры Elasticsearch API

        Returns:
            Результат операции

        ```python
        # Query объект
        query_obj = Term(field="category", value="electronics")
        await es.update_by_query(query=query_obj())  # query_obj() возвращает dict

        # Или сырой dict
        await es.update_by_query(query={"term": {"category": "electronics"}})
        ```
        """
        resolved_alias = self._resolve_alias(base_alias)
        es_method = self._QUERY_OPERATION_METHODS[operation_type](super())
        result = await es_method(index=resolved_alias, query=query, **kwargs)
        return result

    # === ПУБЛИЧНЫЕ МЕТОДЫ: ЧТЕНИЕ ===
    async def get(
        self,
        doc_id: str,
        base_alias: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Получить документ по ID

        Получает один документ по его уникальному идентификатору.

        Особенности:
        - Если документ не найден - бросает NotFoundError
        - Для безопасного получения используйте `get_or_none()`

        Args:
            doc_id: ID документа для получения
            base_alias: Алиас для поиска (если None - дефолтный)
            **kwargs: Дополнительные параметры Elasticsearch get API:
                - _source: bool | str | List[str] - какие поля возвращать
                - stored_fields: List[str] - возвращаемые stored поля
                - routing: str - routing ключ
                - preference: str - предпочтительный шард
                - realtime: bool - реальное время (не из searcher)
                - refresh: bool - принудительно обновить перед чтением
                - version: bool - возвращать версию документа
                - version_type: str - тип версии ("internal", "external", "external_gte")
                - И другие параметры Elasticsearch get API

        Returns:
            Документ (словарь) из поля _source

        Raises:
            NotFoundError: если документ с указанным ID не найден

        Пример:
            ```python
            # Получение документа по ID
            try:
                product = await es.get(
                    doc_id="123",
                    index="products",
                    _source=["name", "base_price", "category"]  # Только нужные поля
                )
                print(f"Найден продукт: {product['name']}")
            except NotFoundError:
                print("Документ не найден")

            # Получение с routing (если используется шардирование)
            user_data = await es.get(
                doc_id="user_456",
                index="users",
                routing="shard_key_123"
            )
            ```

        См. также:
            - `get_or_none()` - безопасное получение (возвращает None если не найден)
            - `mget()` - для получения нескольких документов за один запрос
        """
        resolved_alias = self._resolve_alias(base_alias)
        response = await super().get(index=resolved_alias, id=doc_id, **kwargs)
        return response["_source"]

    async def get_or_none(
        self,
        doc_id: str,
        base_alias: Optional[str] = None,
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """
        Получить документ по ID или None если не найден

        Безопасная версия метода `get()`. Возвращает None вместо исключения,
        если документ с указанным ID не найден.

        Особенности:
        - Не бросает исключение при отсутствии документа
        - Полезен для проверки существования документа без обработки исключений

        Args:
            doc_id: ID документа для получения
            base_alias: Алиас для поиска (если None - дефолтный)
            **kwargs: Дополнительные параметры Elasticsearch get API:
                - _source: bool | str | List[str] - какие поля возвращать
                - stored_fields: List[str] - возвращаемые stored поля
                - routing: str - routing ключ
                - preference: str - предпочтительный шард
                - realtime: bool - реальное время
                - refresh: bool - принудительно обновить перед чтением
                - version: bool - возвращать версию документа
                - И другие параметры Elasticsearch get API

        Returns:
            Документ (словарь) или None, если документ не найден

        Пример:
            ```python
            # Безопасное получение документа
            product = await es.get_or_none(
                doc_id="123",
                index="products"
            )

            if product:
                print(f"Найден продукт: {product['name']}")
            else:
                print("Продукт не найден, можно создавать новый")

            # Проверка существования документа перед обновлением
            existing = await es.get_or_none(doc_id="user_789", index="users")
            if existing is None:
                await es.create(document={"id": "user_789", "name": "New User"})
            ```

        См. также:
            - `get()` - получение с исключением если документ не найден
            - `PydanticESClient.get_or_none()` - версия с валидацией в Pydantic модель
        """
        try:
            return await self.get(doc_id=doc_id, base_alias=base_alias, **kwargs)
        except NotFoundError:
            return None

    async def mget(
        self,
        ids: Optional[str | Sequence[str]] = None,
        base_alias: Optional[str] = None,
        **kwargs,
    ) -> List[Optional[Dict[str, Any]]]:
        """
        Получить несколько документов по ID (multi-get)

        Args:
            ids: Список ID документов для получения
            base_alias: Алиас (если None - дефолтный)
            **kwargs: Дополнительные параметры Elasticsearch mget API:
                - source: bool | str | List[str] - какие поля возвращать (синоним _source)
                - _source: bool | str | List[str] - какие поля возвращать
                - source_includes: List[str] - включаемые поля
                - source_excludes: List[str] - исключаемые поля
                - stored_fields: List[str] - возвращаемые stored поля
                - routing: str - routing ключ
                - preference: str - предпочтительный шард
                - realtime: bool - реальное время
                - refresh: bool - принудительно обновить перед чтением
                - version: bool - возвращать версию документа
                - И другие параметры Elasticsearch mget API

        Returns:
            Список документов (словарей). Если документ не найден,
            в списке будет None на соответствующей позиции.

        Пример:
            ```python
            # Получить несколько документов
            docs = await es.mget(
                ids=["123", "456", "789"],
                index="products",
                _source=["name", "base_price"]
            )

            for i, doc in enumerate(docs):
                if doc:
                    print(f"Документ {ids[i]}: {doc['name']}")
                else:
                    print(f"Документ {ids[i]} не найден")
            ```
        """
        resolved_alias = self._resolve_alias(base_alias)
        response = await super().mget(index=resolved_alias, ids=ids, **kwargs)
        return [doc.get("_source") if doc.get("found") else None for doc in response["docs"]]

    async def search(
        self,
        base_alias: Optional[str] = None,
        body: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Выполнить поисковый запрос

        Основной метод для полнотекстового поиска, фильтрации и агрегаций.

        Особенности:
        - Для построения запросов используйте классы из `es.main_query`
        - Для пагинации используйте параметры `from_` и `size`

        Args:
            base_alias: Алиас для поиска (если None - дефолтный)
            body: Тело поискового запроса (рекомендуется использовать MainQuery)
            **kwargs: Дополнительные параметры Elasticsearch search API:
                - size: int - количество возвращаемых результатов
                - from_: int - смещение для пагинации
                - sort: List | str - сортировка результатов
                - _source: bool | List[str] - фильтрация возвращаемых полей
                - highlight: Dict - подсветка результатов поиска
                - explain: bool - объяснение релевантности
                - timeout: str - таймаут операции ("30s", "1m")
                - track_total_hits: bool | int - точный подсчет общего количества
                - search_after: List - курсор для глубокой пагинации
                - И другие параметры Elasticsearch search API

        Returns:
            Сырой ответ Elasticsearch с результатами поиска

        Пример:
            ```python
            from es.main_query.main import MainQuery
            from es.main_query.query import Match

            # Поиск с использованием MainQuery
            query = MainQuery(
                query=Match(query="smartphone", field="product_name"),
                size=10,
                _source=["product_name", "base_price", "rating"]
            )

            results = await es.search(
                index="products",
                body=query(),
                track_total_hits=True
            )
            ```

        См. также:
            - `MainQuery` - для построения структурированных запросов
            - `count()` - для подсчета документов без возврата результатов
        """
        resolved_alias = self._resolve_alias(base_alias)
        return await super().search(index=resolved_alias, body=body, **kwargs)

    # TODO: убрать из комментариев везде MainQuery, использовать стандартный DSL, AsyncSearch
    async def msearch(
        self,
        searches: Optional[Sequence[Mapping[str, Any]]] = None,
        base_alias: Optional[str] = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Выполнить множественный поиск (multi-search)

        Метод для выполнения нескольких поисковых запросов в одном HTTP-запросе.
        Увеличивает производительность при необходимости выполнить несколько запросов одновременно.

        Особенности:
        - Все запросы выполняются параллельно в одном HTTP-запросе
        - Каждый запрос может иметь свои параметры (size, from_, sort, _source и т.д.)
        - Результаты возвращаются в том же порядке, что и запросы

        Args:
            searches: Список поисковых запросов. Каждый элемент - словарь с телом запроса.
                      Формат: [{"query": {...}, "size": 10}, {"query": {...}, "size": 5}]
                      Можно использовать MainQuery() для генерации запросов.
            base_alias: Алиас для поиска (если None - дефолтный)
            **kwargs: Дополнительные параметры Elasticsearch msearch API:
                - search_type: str - тип поиска ("query_then_fetch", "dfs_query_then_fetch")
                - routing: str - routing ключ для всех запросов
                - preference: str - предпочтительный шард
                - ccs_minimize_roundtrips: bool - минимизация RTT для cross-cluster поиска
                - max_concurrent_searches: int - максимальное количество параллельных поисков
                - rest_total_hits_as_int: bool - возвращать total hits как int (а не объект)
                - allow_no_indices: bool - разрешить отсутствие индексов
                - expand_wildcards: str | List[str] - обработка wildcard в именах индексов
                - ignore_unavailable: bool - игнорировать недоступные индексы
                - ignore_throttled: bool - игнорировать throttled индексы
                - pre_filter_shard_size: int - предварительный фильтр шардов
                - typed_keys: bool - возвращать типизированные ключи в агрегациях
                - include_named_queries_score: bool - включать именованные запросы в оценку
                - project_routing: str - project routing для всех запросов
                - И другие параметры Elasticsearch msearch API

        Returns:
            Список результатов поиска в том же порядке, что и запросы.
            Каждый элемент списка имеет стандартный формат ответа Elasticsearch search.

        Пример:
            ```python
            from es.main_query.main import MainQuery
            from es.main_query.query import Match, Term

            # Создаем несколько запросов
            query1 = MainQuery(
                query=Match(query="smartphone", field="category"),
                size=5,
                _source=["product_name", "base_price"]
            )

            query2 = MainQuery(
                query=Term(field="brand", value="Apple"),
                size=3,
                sort=[{"base_price": {"order": "desc"}}]
            )

            query3 = MainQuery(
                query=Match(query="wireless", field="features"),
                size=10,
                from_=20
            )

            # Выполняем множественный поиск
            results = await es.msearch(
                searches=[query1(), query2(), query3()],
                index="products"
            )

            # Обрабатываем результаты
            for i, result in enumerate(results):
                hits = result["hits"]["hits"]
                print(f"Запрос {i + 1}: найдено {len(hits)} результатов")
                for hit in hits:
                    print(f"  - {hit['_source'].get('product_name', 'Без названия')}")

            # Результат:
            # Запрос 1: найдено 5 результатов
            # Запрос 2: найдено 3 результата
            # Запрос 3: найдено 10 результатов

            # Использование с кастомными параметрами для всех запросов
            results = await es.msearch(
                searches=[query1(), query2()],
                index="products",
                search_type="query_then_fetch",
                routing="user_123",
                rest_total_hits_as_int=True
            )
            ```

        См. также:
            - `search()` - для одиночных поисковых запросов
            - `MainQuery` - для построения структурированных запросов
            - `mget()` - для множественного получения документов по ID
        """
        resolved_alias = self._resolve_alias(base_alias)
        response = await super().msearch(index=resolved_alias, searches=searches, **kwargs)
        return response.get("responses", [])

    async def aggregate(
        self,
        body: Optional[Dict[str, Any]] = None,
        base_alias: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Несмотря на схожесть с search, метод aggregate может пригодиться
        для модели ответа агрегации, отличной от модели ответа поиска документов

        Метод для выполнения аналитических запросов с агрегациями.
        Возвращает сырой ответ Elasticsearch с результатами агрегаций.

        Особенности:
        - Возвращает сырой ответ Elasticsearch с агрегациями
        - Используется для аналитики, статистики, группировок
        - Для pure-агрегаций рекомендуется установить size=0

        Args:
            body: Тело запроса с агрегациями (рекомендуется использовать MainQuery)
            base_alias: Алиас для агрегации (если None - дефолтный)
            **kwargs: Дополнительные параметры Elasticsearch search API:
                - size: int - количество возвращаемых документов
                         Для pure-агрегаций установите size=0
                - timeout: str - таймаут операции
                - track_total_hits: bool | int - точный подсчет общего количества
                - И другие параметры Elasticsearch search API

        Returns:
            Сырой ответ Elasticsearch с результатами агрегаций

        Пример:
            ```python
            from es.main_query.main import MainQuery
            from es.main_query.aggregation import TermsAgg, StatsAgg

            # Pure-агрегация (только статистика, без документов)
            query = MainQuery(
                aggs=[
                    TermsAgg("brands", "brand", size=10),
                    StatsAgg("price_stats", "base_price")
                ],
                size=0  # Важно: size=0 для pure-агрегаций
            )

            result = await es.aggregate(body=query())

            brands = result["aggregations"]["brands"]["buckets"]
            price_stats = result["aggregations"]["price_stats"]

            # Агрегация + первые документы
            query_with_docs = MainQuery(
                query=Match(query="phone", field="category"),
                aggs=[TermsAgg("categories", "category")],
                size=5  # Получаем и документы, и агрегации
            )

            result_with_docs = await es.aggregate(body=query_with_docs())
            hits = result_with_docs["hits"]["hits"]
            aggs = result_with_docs["aggregations"]
            ```
        """
        resolved_alias = self._resolve_alias(base_alias)
        return await super().search(index=resolved_alias, body=body, **kwargs)

    async def count(
        self,
        query: Optional[Mapping[str, Any]] = None,
        base_alias: Optional[str] = None,
        **kwargs,
    ) -> int:
        """
        Подсчет документов по запросу

        Быстрый подсчет количества документов, удовлетворяющих условиям запроса.
        Не возвращает сами документы, только их количество.

        Особенности:
        - Быстрее чем search + подсчет, так как не загружает документы
        - Поддерживает все типы запросов Elasticsearch

        Args:
            query: Запрос для фильтрации документов.
                  Если None - подсчет всех документов в индексе.
                  Рекомендуется использовать Query объекты из es.main_query.
            base_alias: Алиас для подсчета (если None - дефолтный)
            **kwargs: Дополнительные параметры Elasticsearch count API:
                - routing: str | List[str] - routing ключ(и)
                - preference: str - предпочтительный шард
                - timeout: str - таймаут операции ("30s", "1m")
                - terminate_after: int - остановить после N документов
                - allow_no_indices: bool - разрешить отсутствие индексов
                - expand_wildcards: str - обработка wildcard в именах индексов
                - ignore_unavailable: bool - игнорировать недоступные индексы
                - min_score: float - минимальная оценка релевантности
                - И другие параметры Elasticsearch count API

        Returns:
            Количество документов, удовлетворяющих запросу

        Пример:
            ```python
            from es.main_query.query import Term, Range

            # Подсчет всех документов в индексе
            total = await es.count(index="products")

            # Подсчет документов по категории
            electronics_count = await es.count(
                query=Term(field="category", value="electronics")()
            )

            # Подсчет документов в ценовом диапазоне
            affordable = await es.count(
                query=Range(field="base_price", lte=1000)(),
                index="products",
                timeout="10s"
            )
            ```

        См. также:
            - `search()` - для поиска с возвратом документов
            - Query классы в `es.main_query.query` - для построения запросов
        """
        resolved_alias = self._resolve_alias(base_alias)
        response = await super().count(index=resolved_alias, query=query, **kwargs)
        return response["count"]

    # === ПУБЛИЧНЫЕ МЕТОДЫ: ОДИНОЧНЫЕ ОПЕРАЦИИ ===
    async def create(
        self,
        document: Dict[str, Any],
        base_alias: Optional[str] = None,
        id_field: str = ID_FIELD_DEFAULT,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Создать документ (CREATE операция)

        CREATE: создаёт только новый документ. Если документ с таким ID уже существует -
        операция завершится ошибкой (ConflictError).

        Отличие от INDEX операции:
        - CREATE: только создание, ошибка если существует
        - INDEX: создание или замена (upsert)

        Args:
            document: Документ для создания (словарь)
            base_alias: Алиас (если None - дефолтный)
            id_field: Поле документа, содержащее ID (по умолчанию: "id").
                     Должно быть указано для CREATE операции.
            **kwargs: Дополнительные параметры Elasticsearch create API:
                - refresh: RefreshType - когда сделать изменения видимыми
                          "true" - немедленно, "false" - никогда, "wait_for" - дождаться
                - timeout: str - таймаут операции ("30s", "1m", "500ms")
                - version: int - версия для optimistic concurrency control
                - if_seq_no: int - номер последовательности
                - if_primary_term: int - primary term
                - routing: str - routing ключ
                - pipeline: str - pipeline для обработки документа
                - И другие параметры Elasticsearch create API

        Returns:
            Сырой ответ ES

        Raises:
            ConflictError: если документ с таким ID уже существует

        Пример:
            ```python
            # Создание документа с проверкой уникальности ID
            await es.create(
                document={"id": "123", "name": "New Product", "base_price": 99.99},
                index="products",
                id_field="id",  # Поле содержащее ID (по умолчанию)
                refresh="wait_for",
                routing="category_123"
            )
            ```

        См. также:
            - `index()` - для создания или замены документов
            - `bulk_create()` - для массового создания
        """
        return await self._single_execute(
            document=document,
            operation_type=OperationType.CREATE,
            base_alias=base_alias,
            id_field=id_field,
            **kwargs,
        )

    async def index(
        self,
        document: Dict[str, Any],
        base_alias: Optional[str] = None,
        id_field: str = ID_FIELD_DEFAULT,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Индексировать документ (INDEX операция)

        INDEX: создаёт или заменяет документ. Если документ с таким ID уже существует -
        он будет полностью перезаписан (upsert).

        Отличие от CREATE операции:
        - INDEX: создание или замена (upsert)
        - CREATE: только создание, ошибка если существует

        Args:
            document: Документ для индексации (словарь)
            base_alias: Алиас (если None - дефолтный)
            id_field: Поле документа, содержащее ID (по умолчанию: "id").
                     Если None - Elasticsearch сгенерирует ID автоматически.
            **kwargs: Дополнительные параметры Elasticsearch index API:
                - refresh: RefreshType - когда сделать изменения видимыми
                          "true" - немедленно, "false" - никогда, "wait_for" - дождаться
                - timeout: str - таймаут операции ("30s", "1m", "500ms")
                - version: int - версия для optimistic concurrency control
                - if_seq_no: int - номер последовательности
                - if_primary_term: int - primary term
                - routing: str - routing ключ
                - pipeline: str - pipeline для обработки документа
                - require_alias: bool - требовать, чтобы индекс был алиасом
                - op_type: str - тип операции ("index" или "create")
                - И другие параметры Elasticsearch index API

        Returns:
            Сырой ответ ES

        Пример:
            ```python
            # Индексация документа (создание или замена)
            await es.index(
                document={"id": "123", "name": "Product", "base_price": 149.99},
                index="products",
                refresh=True,
                timeout="30s"
            )
            ```

        См. также:
            - `create()` - только создание новых документов
            - `bulk_index()` - для массовой индексации
        """
        return await self._single_execute(
            document=document,
            operation_type=OperationType.INDEX,
            base_alias=base_alias,
            id_field=id_field,
            **kwargs,
        )

    async def update(
        self,
        document: Dict[str, Any],
        base_alias: Optional[str] = None,
        id_field: str = ID_FIELD_DEFAULT,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Обновить документ (UPDATE операция)

        UPDATE: обновляет существующий документ. Если документ не существует -
        операция завершится ошибкой (NotFoundError).

        Отличие от INDEX операции:
        - UPDATE: обновление существующего документа (ошибка если не существует)
        - INDEX: создание или полная замена (upsert)

        Особенности:
        - Обновляет весь документ (полная замена)
        - Для частичного обновления используйте `partial_update()`
        - Документ должен содержать ID

        Args:
            document: Документ с обновлениями (полностью заменяет существующий)
            base_alias: Алиас (если None - дефолтный)
            id_field: Поле документа, содержащее ID (по умолчанию: "id")
            **kwargs: Дополнительные параметры Elasticsearch update API:
                - refresh: RefreshType - когда сделать изменения видимыми
                          "true" - немедленно, "false" - никогда, "wait_for" - дождаться
                - timeout: str - таймаут операции ("30s", "1m", "500ms")
                - retry_on_conflict: int - количество попыток при конфликте версий
                - if_seq_no: int - номер последовательности для optimistic concurrency control
                - if_primary_term: int - primary term для контроля версий
                - routing: str - routing ключ
                - version: int - версия документа
                - doc_as_upsert: bool - создавать документ если не существует
                - detect_noop: bool - определять no-op операции
                - И другие параметры Elasticsearch update API

        Returns:
            Сырой ответ ES

        Raises:
            NotFoundError: если документ не существует

        Пример:
            ```python
            # Полное обновление документа
            await es.update(
                document={"id": "123", "name": "Updated Product", "base_price": 199.99, "stock": 50},
                index="products",
                refresh="wait_for",
                retry_on_conflict=3
            )
            ```

        См. также:
            - `partial_update()` - для частичного обновления полей
            - `index()` - для создания или полной замены
            - `bulk_update()` - для массового обновления
        """
        return await self._single_execute(
            document=document,
            operation_type=OperationType.UPDATE,
            base_alias=base_alias,
            id_field=id_field,
            **kwargs,
        )

    async def delete(
        self,
        document: Dict[str, Any],
        base_alias: Optional[str] = None,
        id_field: str = ID_FIELD_DEFAULT,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Удалить документ (DELETE операция)

        DELETE: удаляет документ. Если документ не существует - операция считается успешной
        (не бросает исключение).

        Особенности:
        - Удаление идемпотентно: повторное удаление несуществующего документа - успешно
        - Для удаления по ID без документа используйте `delete_by_id()`
        - Для массового удаления используйте `bulk_delete()` или `bulk_delete_by_ids()`

        Args:
            document: Документ для удаления (должен содержать ID)
            base_alias: Алиас (если None - дефолтный)
            id_field: Поле документа, содержащее ID (по умолчанию: "id")
            **kwargs: Дополнительные параметры Elasticsearch delete API:
                - refresh: RefreshType - когда сделать изменения видимыми
                          "true" - немедленно, "false" - никогда, "wait_for" - дождаться
                - timeout: str - таймаут операции ("30s", "1m", "500ms")
                - version: int - версия для optimistic concurrency control
                - if_seq_no: int - номер последовательности
                - if_primary_term: int - primary term
                - routing: str - routing ключ
                - wait_for_active_shards: str | int - ждать активных шардов
                - require_alias: bool - требовать, чтобы индекс был алиасом
                - И другие параметры Elasticsearch delete API

        Returns:
            Сырой ответ ES

        Пример:
            ```python
            # Удаление документа
            await es.delete(
                document={"id": "123", "name": "Product to delete"},
                index="products",
                refresh=True,
                timeout="10s"
            )
            ```

        См. также:
            - `delete_by_id()` - удаление по ID без документа
            - `bulk_delete()` - массовое удаление по документам
            - `bulk_delete_by_ids()` - массовое удаление по списку ID
            - `delete_by_query()` - удаление по запросу
        """
        return await self._single_execute(
            document=document,
            operation_type=OperationType.DELETE,
            base_alias=base_alias,
            id_field=id_field,
            **kwargs,
        )

    async def delete_by_id(
        self,
        doc_id: str,
        id_field: str = ID_FIELD_DEFAULT,
        base_alias: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Удалить документ по ID

        Удобная обертка над `delete()` для удаления по ID без необходимости
        создавать полный документ.

        Особенности:
        - Удаление идемпотентно: повторное удаление несуществующего документа - успешно
        - Использует _write алиас по умолчанию
        - Для удаления нескольких документов используйте `bulk_delete_by_ids()`

        Args:
            doc_id: ID документа для удаления
            id_field: Поле, содержащее ID (по умолчанию: "id")
                    Используется только для создания временного документа.
            base_alias: Алиас (если None - дефолтный)
            **kwargs: Дополнительные параметры Elasticsearch delete API:
                - refresh: RefreshType - когда сделать изменения видимыми
                          "true" - немедленно, "false" - никогда, "wait_for" - дождаться
                - timeout: str - таймаут операции ("30s", "1m", "500ms")
                - version: int - версия для optimistic concurrency control
                - if_seq_no: int - номер последовательности
                - if_primary_term: int - primary term
                - routing: str - routing ключ
                - wait_for_active_shards: str | int - ждать активных шардов
                - require_alias: bool - требовать, чтобы индекс был алиасом
                - И другие параметры Elasticsearch delete API

        Returns:
            Сырой ответ ES

        Пример:
            ```python
            # Удаление по ID
            await es.delete_by_id(
                doc_id="123",
                index="products",
                refresh=True
            )

            # Удаление с кастомным полем ID
            await es.delete_by_id(
                doc_id="P001",
                id_field="sku",  # Используем поле sku как ID
                index="products",
                timeout="15s"
            )

            # Удаление с дополнительными параметрами
            await es.delete_by_id(
                doc_id="user_456",
                index="users",
                routing="shard_key_123",  # Для правильного шардирования
                version=5  # Удалить только если версия = 5
            )
            ```

        См. также:
            - `delete()` - удаление по полному документу
            - `bulk_delete_by_ids()` - массовое удаление по списку ID
            - `bulk_delete()` - массовое удаление по документам
        """
        document = {id_field: doc_id}
        return await self._single_execute(
            document=document,
            operation_type=OperationType.DELETE,
            base_alias=base_alias,
            id_field=id_field,
            **kwargs,
        )

    @staticmethod
    def _create_update_script(updates: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Создать Painless script для частичного обновления

        Генерирует читаемые имена параметров на основе имен полей.
        Пример: {"base_price": 99.99} → параметр field_price

        Заменяет недопустимые символы на '_' для безопасного использования в Painless script.

        Args:
            updates: Словарь {поле: новое_значение}
                    Если None или пустой - возвращает None

        Returns:
            Словарь с параметрами script для Elasticsearch или None
        """
        if not updates:
            return None

        script_source = []
        script_params = {}

        for field, value in updates.items():
            safe_field = re.sub(r"[.[\] ]", "_", field)
            param_name = f"field_{safe_field}"

            script_source.append(f"ctx._source.{field} = params.{param_name};")
            script_params[param_name] = value

        return {"source": " ".join(script_source), "params": script_params, "lang": "painless"}

    async def partial_update(
        self,
        doc_id: str,
        updates: Optional[Dict[str, Any]] = None,
        base_alias: Optional[str] = None,
        script: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Optional[Dict[str, Any]]:
        """
        Частичное обновление документа через Painless script

        Args:
            doc_id: ID документа для обновления
            updates: Словарь с обновлениями (только изменяемые поля).
                    Используется только если script=None.
                    Если None и script=None - метод завершится без ошибок, ничего не обновив.
            base_alias: Алиас (если None - дефолтный)
            script: Кастомный Painless script для обновления.
                   Если None - будет создан автоматически из updates.
                   Если updates тоже None или пустой - метод завершится без ошибок.
                   Формат: {"source": "...", "params": {...}, "lang": "painless"}
            **kwargs: Дополнительные параметры Elasticsearch update API:
                - refresh: RefreshType - когда сделать изменения видимыми
                          "true" - немедленно, "false" - никогда, "wait_for" - дождаться
                - timeout: str - таймаут операции ("30s", "1m", "500ms")
                - retry_on_conflict: int - количество попыток при конфликте версий
                - if_seq_no: int - номер последовательности для optimistic concurrency control
                - if_primary_term: int - primary term для контроля версий
                - routing: str - routing ключ
                - version: int - версия документа
                - И другие параметры Elasticsearch update API

        Returns:
            Сырой ответ ES

        Примеры:
            ```python
            # 1. Автоматический script из updates
            await es.partial_update(
                doc_id="123",
                updates={"base_price": 99.99, "stock": 50},
                index="products",
                refresh="wait_for"
            )

            # 2. Кастомный script (updates игнорируется)
            await es.partial_update(
                doc_id="456",
                script={
                    "source": "ctx._source.views += params.increment",
                    "params": {"increment": 1},
                    "lang": "painless"
                },
                retry_on_conflict=3
            )

            # 3. Ничего не обновлять - просто завершится
            await es.partial_update(doc_id="789")
            ```
        """
        final_script = script or self._create_update_script(updates)
        if not final_script:
            return None

        resolved_alias = self._resolve_alias(base_alias)
        operation_kwargs = self._map_to_es_kwargs(doc_id=doc_id, **kwargs)
        result = await super().update(index=resolved_alias, script=final_script, **operation_kwargs)
        return result

    # === ПУБЛИЧНЫЕ МЕТОДЫ: МАССОВЫЕ ОПЕРАЦИИ ===
    async def bulk_index(
        self,
        documents: List[Dict[str, Any]],
        base_alias: Optional[str] = None,
        id_field: str | None = ID_FIELD_DEFAULT,
        raise_on_error: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Массовая индексация документов

        INDEX: создаёт или заменяет документ. Если документ с таким ID уже существует - он будет перезаписан.

        Args:
            documents: Список документов для индексации
            base_alias: Алиас (если None - дефолтный)
            id_field: Поле документа, содержащее ID (по умолчанию: "id").
                     Если None - Elasticsearch сгенерирует ID автоматически.
            raise_on_error: Бросать исключение при ошибках в bulk операции.
            **kwargs: Дополнительные параметры Elasticsearch bulk API:
                - refresh: RefreshType - когда сделать изменения видимыми
                - timeout: str - таймаут операции ("30s", "1m", "500ms")
                - pipeline: str - pipeline для обработки документов
                - И другие параметры bulk API.

        Returns:
            Сырой ответ ES

        Пример:
            ```python
            # Индексация с автоматическими ID
            await es.bulk_index(
                documents=[{"name": "Product 1"}, {"name": "Product 2"}],
                id_field=None,  # ES сам сгенерирует ID
                refresh=True
            )

            # Индексация с кастомным полем ID
            await es.bulk_index(
                documents=[
                    {"sku": "P001", "name": "Product 1"},
                    {"sku": "P002", "name": "Product 2"}
                ],
                id_field="sku",  # Используем поле sku как ID
                raise_on_error=True
            )
            ```
        """
        return await self._bulk_execute(
            documents=documents,
            operation_type=OperationType.INDEX,
            base_alias=base_alias,
            id_field=id_field,
            raise_on_error=raise_on_error,
            **kwargs,
        )

    async def bulk_create(
        self,
        documents: List[Dict[str, Any]],
        base_alias: Optional[str] = None,
        id_field: str | None = ID_FIELD_DEFAULT,
        raise_on_error: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Массовое создание документов

        CREATE: создаёт только новый документ. Если документ с таким ID уже существует - операция завершится ошибкой.

        Args:
            documents: Список документов для создания
            base_alias: Алиас (если None - дефолтный)
            id_field: Поле документа, содержащее ID (по умолчанию: "id").
                     Должно быть указано для CREATE операции.
            raise_on_error: Бросать исключение при ошибках в bulk операции.
            **kwargs: Дополнительные параметры Elasticsearch bulk API.

        Returns:
            Сырой ответ ES

        Пример:
            ```python
            # Создание документов с проверкой уникальности ID
            await es.bulk_create(
                documents=[
                    {"id": "123", "name": "Unique Product 1"},
                    {"id": "124", "name": "Unique Product 2"}
                ],
                raise_on_error=True  # Упадёт если документы с такими ID уже существуют
            )
            ```
        """
        return await self._bulk_execute(
            documents=documents,
            operation_type=OperationType.CREATE,
            base_alias=base_alias,
            id_field=id_field,
            raise_on_error=raise_on_error,
            **kwargs,
        )

    async def bulk_update(
        self,
        documents: List[Dict[str, Any]],
        base_alias: Optional[str] = None,
        id_field: str | None = ID_FIELD_DEFAULT,
        raise_on_error: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Массовое обновление документов

        UPDATE: обновляет существующий документ. Если документ не существует - операция завершится ошибкой.

        Args:
            documents: Список документов с обновлениями. Каждый документ должен содержать ID.
            base_alias: Алиас (если None - дефолтный)
            id_field: Поле документа, содержащее ID (по умолчанию: "id").
                     Обязательно должно быть указано.
            raise_on_error: Бросать исключение при ошибках в bulk операции.
            **kwargs: Дополнительные параметры Elasticsearch bulk API.

        Returns:
            Сырой ответ ES

        Пример:
            ```python
            # Обновление нескольких документов
            await es.bulk_update(
                documents=[
                    {"id": "123", "base_price": 99.99},
                    {"id": "124", "stock": 50}
                ],
                refresh=True
            )
            ```
        """
        return await self._bulk_execute(
            documents=documents,
            operation_type=OperationType.UPDATE,
            base_alias=base_alias,
            id_field=id_field,
            raise_on_error=raise_on_error,
            **kwargs,
        )

    async def bulk_delete(
        self,
        documents: List[Dict[str, Any]],
        base_alias: Optional[str] = None,
        id_field: str | None = ID_FIELD_DEFAULT,
        raise_on_error: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Массовое удаление документов по самим документам.

        DELETE: удаляет документ. Если документ не существует - операция считается успешной.

        Args:
            documents: Список документов для удаления. Каждый документ должен содержать ID.
            base_alias: Алиас (если None - дефолтный)
            id_field: Поле документа, содержащее ID (по умолчанию: "id").
            raise_on_error: Бросать исключение при ошибках в bulk операции.
            **kwargs: Дополнительные параметры Elasticsearch bulk API.

        Returns:
            Сырой ответ ES

        Пример:
            ```python
            # Удаление документов по полю "sku"
            await es.bulk_delete(
                documents=[
                    {"sku": "P001"},
                    {"sku": "P002"}
                ],
                id_field="sku",
                refresh=True
            )
            ```
        """
        return await self._bulk_execute(
            documents=documents,
            operation_type=OperationType.DELETE,
            base_alias=base_alias,
            id_field=id_field,
            raise_on_error=raise_on_error,
            **kwargs,
        )

    async def bulk_delete_by_ids(
        self,
        ids: List[str],
        base_alias: Optional[str] = None,
        raise_on_error: bool = False,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Массовое удаление документов по их ID.

        DELETE: удаляет документ. Если документ не существует - операция считается успешной.

        Args:
            ids: Список ID документов для удаления
            base_alias: Алиас (если None - дефолтный)
            raise_on_error: Бросать исключение при ошибках в bulk операции.
            **kwargs: Дополнительные параметры Elasticsearch bulk API.

        Returns:
            Сырой ответ ES

        Пример:
            ```python
            # Удаление по списку ID
            await es.bulk_delete_by_ids(
                ids=["123", "124", "125"],
                refresh=True,
                raise_on_error=True
            )
            ```
        """
        # Преобразуем IDs в документы с дефолтным полем ID
        documents = [{ID_FIELD_DEFAULT: _id} for _id in ids]

        return await self._bulk_execute(
            documents=documents,
            operation_type=OperationType.DELETE,
            base_alias=base_alias,
            id_field=ID_FIELD_DEFAULT,  # Используем дефолтное поле
            raise_on_error=raise_on_error,
            **kwargs,
        )

    # === ПУБЛИЧНЫЕ МЕТОДЫ: ОПЕРАЦИИ ПО ЗАПРОСУ ===
    async def update_by_query(
        self,
        query: Mapping[str, Any],
        base_alias: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Обновить документы по запросу

        Args:
            query: Query dict для фильтрации документов. Должен быть результатом вызова Query объекта:
            base_alias: базовый алиас (если None - дефолтный)
            **kwargs: Дополнительные параметры Elasticsearch update_by_query API.
                     См. подробности в _by_query_execute().

                     Важные параметры:
                     - script: Dict[str, Any] - Painless script для обновления документов
                     - conflicts: str - "abort" (прервать при конфликте) или "proceed" (продолжить)
                     - refresh: bool - немедленно обновить индекс после операции
                     - timeout: str - таймаут операции ("30s", "1m")
                     - wait_for_completion: bool - False для асинхронного выполнения
                     - max_docs: int - ограничить количество обновляемых документов
                     - slices: int | "auto" - параллельная обработка для ускорения

        Returns:
            Сырой ответ ES

        Пример:
            ```python
            # Обновить все электронные товары, увеличив счётчик просмотров
            await es.update_by_query(
                query=Term(field="category", value="electronics")(),
                script={
                    "source": "ctx._source.view_count += params.increment",
                    "params": {"increment": 1}
                },
                refresh=True,
                conflicts="proceed"
            )
            ```
        """
        return await self._by_query_execute(
            query=query,
            operation_type=QueryOperationType.UPDATE_BY_QUERY,
            base_alias=base_alias,
            **kwargs,
        )

    async def delete_by_query(
        self,
        query: Mapping[str, Any],
        base_alias: Optional[str] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Удалить документы по запросу

        Args:
            query: Query dict для фильтрации документов. Должен быть результатом вызова Query объекта:
            base_alias: Базовый алиас (если None - дефолтный)
            **kwargs: Дополнительные параметры Elasticsearch delete_by_query API.
                     См. подробности в _by_query_execute().

                     Важные параметры:
                     - refresh: bool - немедленно обновить индекс после удаления
                     - timeout: str - таймаут операции ("30s", "1m")
                     - conflicts: str - "abort" или "proceed"
                     - wait_for_completion: bool - False для асинхронного выполнения
                     - max_docs: int - ограничить количество удаляемых документов

        Returns:
            Сырой ответ ES

        Пример:
            ```python
            # Удалить все недоступные товары
            await es.delete_by_query(
                query=Term(field="is_available", value=False)(),
                refresh=True,
                timeout="2m"
            )
            ```
        """
        return await self._by_query_execute(
            query=query,
            operation_type=QueryOperationType.DELETE_BY_QUERY,
            base_alias=base_alias,
            **kwargs,
        )

    # === ПУБЛИЧНЫЕ МЕТОДЫ: УПРАВЛЕНИЕ ИНДЕКСАМИ ===
    async def refresh_index(self, base_alias: Optional[str] = None) -> None:
        """
        Принудительное обновление индекса(ов)

        Без refresh поиск может не найти только что добавленные документы
        в течение refresh_interval (настраивается в маппинге индекса).

        Особенности:
        - Если алиас указывает на несколько индексов, обновляются все соответствующие индексы

        Пример использования:
        ```python
        await es.bulk_index(documents) # Документы индексируются
        await es.refresh_index() # Принудительно обновляем все индексы, соответствующих алиасу по умолчанию
        results = await es.search(query) # Новые документы уже доступны для поиска
        ```

        Args:
            base_alias: Базовый алиас (если None - дефолтный)
        """
        resolved_alias = self._resolve_alias(base_alias)
        indices = await self.get_indices_by_alias(resolved_alias)
        await self.indices.refresh(index=",".join(indices))
