from typing import Any, Dict, List, Mapping, Optional, Sequence, Type, get_args, get_origin

from es.clients.base import BaseESClient
from es.clients.models.document import OperationType
from es.clients.models.pydantic_ import DocumentResult, SearchResult
from es.constants import ID_FIELD_DEFAULT
from pydantic import BaseModel


class PydanticESClient(BaseESClient):
    """
    Клиент для работы с Elasticsearch и Pydantic моделями

    Особенности:
    - Может работать с любой Pydantic моделью
    - Может иметь дефолтную модель (опционально)
    - Автоматическая валидация и сериализация
    - Типизированные результаты операций
    """

    def __init__(
        self,
        hosts: Optional[List[str]] = None,
        default_alias: Optional[str] = None,
        response_model: Optional[Type[BaseModel]] = None,
        **kwargs,
    ):
        """
        Инициализация клиента Elasticsearch для работы с Pydantic моделями

        Args:
            hosts: Список URL нод Elasticsearch (например: ["http://localhost:9200"])
            default_alias: Дефолтный индекс для операций (можно переопределять в методах)
            response_model: Дефолтная Pydantic модель (опционально)
            **kwargs: Дополнительные параметры для AsyncElasticsearch

        Примеры использования:
        ```python
        # Клиент с дефолтной моделью (для одного типа документов)
        product_es = PydanticESClient(
            hosts=["http://localhost:9200"],
            default_alias="products",
            response_model=Product,  # Дефолтная модель
        )

        # Универсальный клиент (для разных типов документов)
        universal_es = PydanticESClient(hosts=["http://localhost:9200"])
        ```
        """
        super().__init__(hosts, default_alias, **kwargs)
        self._response_model = response_model

    def _resolve_response_model(
        self,
        response_model: Optional[Type[BaseModel]] = None,
    ) -> Type[BaseModel]:
        """
        Разрешение класса модели

        Args:
            response_model: Явно указанный класс модели (если None - используется дефолтный)

        Returns:
            Класс Pydantic модели

        Raises:
            ValueError: если не указана модель и нет дефолтной
        """
        resolved_model = response_model or self._response_model
        if not resolved_model:
            raise ValueError(
                "Model class must be specified either in method or in client initialization. "
                "Use either: 1) response_model parameter in method, "
                "or 2) response_model parameter in PydanticESClient constructor."
            )
        return resolved_model

    @staticmethod
    def _process_es_response(results: List[Dict[str, Any]], operation: OperationType) -> List[DocumentResult]:
        """Преобразовать ответ ES в DocumentResult"""
        # TODO: нельзя ли получить operation из result?
        return [
            DocumentResult(
                id=result["_id"],
                index=result["_index"],
                version=result.get("_version", 1),
                operation=operation,
                seq_no=result.get("_seq_no"),
                primary_term=result.get("_primary_term"),
            )
            for result in results
        ]

    @staticmethod
    def _is_pydantic_model_type(annotation) -> bool:
        """
        Проверить, является ли аннотация типом Pydantic модели

        Args:
            annotation: Аннотация типа из field_info.annotation

        Returns:
            True если тип является Pydantic моделью (или Optional[Pydantic модель])
        """
        # Убрать Optional если есть
        if get_origin(annotation) is Optional:
            args = get_args(annotation)
            annotation = args[0] if args else annotation

        try:
            # Является ли тип классом и подклассом BaseModel
            return isinstance(annotation, type) and issubclass(annotation, BaseModel)
        except (TypeError, AttributeError):
            return False  # Если annotation не класс (например, Union[int, str])

    def _get_source_from_model(self, response_model: Type[BaseModel], prefix: str = "") -> List[str]:
        """
        Получить список полей для Elasticsearch _source из Pydantic модели

        Включает все поля, кроме:
        1. Поля с Field(exclude=True)
        2. Вычисляемые поля (@computed_field)

        Рекурсивно обрабатывает поля, которые сами являются Pydantic моделями.

        Args:
            response_model: Pydantic модель
            prefix: Префикс для вложенных полей (для рекурсии)

        Returns:
            Список полей для _source

        Пример:
            ```python
            class Dimensions(BaseModel):
                width: float
                height: float
                depth: float = Field(exclude=True)  # Не включаем

            class Product(BaseModel):
                name: str
                price: float
                dimensions: Dimensions  # Рекурсивно развернется
                secret_code: str = Field(exclude=True)  # Секретный код

                @computed_field
                @property
                def area(self) -> float:
                    return self.dimensions.width * self.dimensions.height

            fields = get_source_filter_from_model(Product)
            # ['name', 'price', 'dimensions.width', 'dimensions.height']
            # НЕ включает: depth (exclude=True), secret_code (exclude=True), area (computed_field)
            ```
        """
        fields: List[str] = []

        # Вычисляемые поля
        computed_fields = getattr(response_model, "model_computed_fields", {})

        for field_name, field_info in response_model.model_fields.items():
            # Проверяем exclude через Field(exclude=True)
            if getattr(field_info, "exclude", False) or field_name in computed_fields:
                continue

            full_name = f"{prefix}{field_name}" if prefix else field_name

            # Проверяем, является ли поле Pydantic моделью
            if self._is_pydantic_model_type(field_info.annotation):
                # Рекурсивно обрабатываем вложенную модель
                nested_prefix = f"{full_name}."
                nested_fields = self._get_source_from_model(field_info.annotation, prefix=nested_prefix)
                fields.extend(nested_fields)
            else:
                fields.append(full_name)  # Простое поле или список/словарь

        return fields

    # === МЕТОДЫ ЧТЕНИЯ С МОДЕЛЯМИ ===
    async def get(
        self,
        doc_id: str,
        response_model: Optional[Type[BaseModel]] = None,
        base_alias: Optional[str] = None,
        use_read_alias: bool = True,
        **kwargs,
    ) -> BaseModel:
        resolved_model = self._resolve_response_model(response_model)
        kwargs.setdefault("_source", self._get_source_from_model(resolved_model))
        doc_dict = await super().get(
            doc_id=doc_id,
            base_alias=base_alias,
            use_read_alias=use_read_alias,
            **kwargs,
        )
        return resolved_model.model_validate(doc_dict)

    async def get_or_none(
        self,
        doc_id: str,
        response_model: Optional[Type[BaseModel]] = None,
        base_alias: Optional[str] = None,
        use_read_alias: bool = True,
        **kwargs,
    ) -> Optional[BaseModel]:
        resolved_model = self._resolve_response_model(response_model)
        kwargs.setdefault("_source", self._get_source_from_model(resolved_model))

        doc_dict = await super().get_or_none(
            doc_id=doc_id,
            base_alias=base_alias,
            use_read_alias=use_read_alias,
            **kwargs,
        )

        if doc_dict is None:
            return None

        return resolved_model.model_validate(doc_dict)

    async def mget(
        self,
        ids: Optional[str | Sequence[str]] = None,
        response_model: Optional[Type[BaseModel]] = None,
        base_alias: Optional[str] = None,
        use_read_alias: bool = True,
        **kwargs,
    ) -> List[Optional[BaseModel]]:
        resolved_model = self._resolve_response_model(response_model)
        kwargs.setdefault("_source", self._get_source_from_model(resolved_model))

        docs = await super().mget(
            ids=ids,
            base_alias=base_alias,
            use_read_alias=use_read_alias,
            **kwargs,
        )

        result = []
        for doc in docs:
            if doc is None:
                result.append(None)
            else:
                result.append(resolved_model.model_validate(doc))

        return result

    async def search(
        self,
        base_alias: Optional[str] = None,
        body: Optional[Dict[str, Any]] = None,
        response_model: Optional[Type[BaseModel]] = None,
        use_read_alias: bool = True,
        **kwargs,
    ) -> SearchResult:
        resolved_model = self._resolve_response_model(response_model)
        kwargs.setdefault("_source", self._get_source_from_model(resolved_model))
        response = await super().search(
            base_alias=base_alias,
            body=body,
            use_read_alias=use_read_alias,
            **kwargs,
        )

        hits_data = response["hits"]["hits"]
        sources = [resolved_model.model_validate(hit["_source"]) for hit in hits_data]

        return SearchResult(
            sources=sources,
            total=response["hits"]["total"]["value"],
            took=response["took"],
        )

    async def msearch(
        self,
        *,
        searches: Optional[Sequence[Mapping[str, Any]]] = None,
        response_models: Optional[Sequence[Type[BaseModel]]] = None,
        base_alias: Optional[str] = None,
        use_read_alias: bool = True,
        **kwargs,
    ) -> List[SearchResult]:
        if not searches:
            raise ValueError("Parameter 'searches' cannot be empty")

        if response_models is None:
            # Дефолтная модель для всех запросов
            default_model = self._resolve_response_model(None)
            models = [default_model] * len(searches)
        elif len(response_models) == 1:
            # Одна модель для всех запросов
            models = list(response_models) * len(searches)
        elif len(response_models) == len(searches):
            # Отдельная модель для каждого запроса
            models = list(response_models)
        else:
            raise ValueError(
                f"Number of response models ({len(response_models)}) must match "
                f"number of searches ({len(searches)}) or be 1 for all searches"
            )

        # Выполняем msearch через родительский метод
        raw_results = await super().msearch(
            searches=searches, base_alias=base_alias, use_read_alias=use_read_alias, **kwargs
        )

        results = []
        for i, (raw_result, model) in enumerate(zip(raw_results, models)):
            hits_data = raw_result["hits"]["hits"]

            sources = []
            for hit in hits_data:
                source = hit.get("_source")
                if not source:
                    continue
                sources.append(model.model_validate(source))

            results.append(
                SearchResult(
                    sources=sources,
                    total=raw_result["hits"]["total"]["value"],
                    took=raw_result["took"],
                )
            )

        return results

    # === ПУБЛИЧНЫЕ МЕТОДЫ: ОДИНОЧНЫЕ ОПЕРАЦИИ ===
    async def create(
        self,
        document: BaseModel,
        base_alias: Optional[str] = None,
        use_write_alias: bool = True,
        id_field: str = ID_FIELD_DEFAULT,
        **kwargs,
    ) -> List[DocumentResult]:
        results = await super().create(
            document=document.model_dump(),
            base_alias=base_alias,
            use_write_alias=use_write_alias,
            id_field=id_field,
            **kwargs,
        )
        return self._process_es_response(results, OperationType.CREATE)

    async def index(
        self,
        document: BaseModel,
        base_alias: Optional[str] = None,
        use_write_alias: bool = True,
        id_field: str = ID_FIELD_DEFAULT,
        **kwargs,
    ) -> List[DocumentResult]:
        results = await super().index(
            document=document.model_dump(),
            base_alias=base_alias,
            use_write_alias=use_write_alias,
            id_field=id_field,
            **kwargs,
        )
        return self._process_es_response(results, OperationType.INDEX)

    async def update(
        self,
        document: BaseModel,
        base_alias: Optional[str] = None,
        use_write_alias: bool = True,
        id_field: str = ID_FIELD_DEFAULT,
        **kwargs,
    ) -> List[DocumentResult]:
        results = await super().update(
            document=document.model_dump(),
            base_alias=base_alias,
            use_write_alias=use_write_alias,
            id_field=id_field,
            **kwargs,
        )
        return self._process_es_response(results, OperationType.UPDATE)

    async def delete(
        self,
        document: BaseModel,
        base_alias: Optional[str] = None,
        use_write_alias: bool = True,
        id_field: str = ID_FIELD_DEFAULT,
        **kwargs,
    ) -> List[DocumentResult]:
        results = await super().delete(
            document=document.model_dump(),
            base_alias=base_alias,
            use_write_alias=use_write_alias,
            id_field=id_field,
            **kwargs,
        )
        return self._process_es_response(results, OperationType.DELETE)

    async def delete_by_id(
        self,
        doc_id: str,
        base_alias: Optional[str] = None,
        use_write_alias: bool = True,
        **kwargs,
    ) -> List[DocumentResult]:
        results = await super().delete_by_id(
            doc_id=doc_id,
            base_alias=base_alias,
            use_write_alias=use_write_alias,
            **kwargs,
        )
        return self._process_es_response(results, OperationType.DELETE)

    async def partial_update(
        self,
        doc_id: str,
        updates: Optional[Dict[str, Any]] = None,
        base_alias: Optional[str] = None,
        use_write_alias: bool = True,
        script: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> List[DocumentResult]:
        results = await super().partial_update(
            doc_id=doc_id,
            updates=updates,
            base_alias=base_alias,
            use_write_alias=use_write_alias,
            script=script,
            **kwargs,
        )
        return self._process_es_response(results, OperationType.UPDATE)

    # === ПУБЛИЧНЫЕ МЕТОДЫ: МАССОВЫЕ ОПЕРАЦИИ ===
    async def bulk_index(
        self,
        documents: List[BaseModel],
        base_alias: Optional[str] = None,
        use_write_alias: bool = True,
        id_field: str | None = ID_FIELD_DEFAULT,
        raise_on_error: bool = False,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        return await super().bulk_index(
            documents=[d.model_dump() for d in documents],
            operation_type=OperationType.INDEX,
            base_alias=base_alias,
            use_write_alias=use_write_alias,
            id_field=id_field,
            raise_on_error=raise_on_error,
            **kwargs,
        )

    async def bulk_create(
        self,
        documents: List[BaseModel],
        base_alias: Optional[str] = None,
        use_write_alias: bool = True,
        id_field: str | None = ID_FIELD_DEFAULT,
        raise_on_error: bool = False,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        return await super().bulk_create(
            documents=[d.model_dump() for d in documents],
            operation_type=OperationType.CREATE,
            base_alias=base_alias,
            use_write_alias=use_write_alias,
            id_field=id_field,
            raise_on_error=raise_on_error,
            **kwargs,
        )

    async def bulk_update(
        self,
        documents: List[BaseModel],
        base_alias: Optional[str] = None,
        use_write_alias: bool = True,
        id_field: str | None = ID_FIELD_DEFAULT,
        raise_on_error: bool = False,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        return await super().bulk_update(
            documents=[d.model_dump() for d in documents],
            operation_type=OperationType.UPDATE,
            base_alias=base_alias,
            use_write_alias=use_write_alias,
            id_field=id_field,
            raise_on_error=raise_on_error,
            **kwargs,
        )

    async def bulk_delete(
        self,
        documents: List[BaseModel],
        base_alias: Optional[str] = None,
        use_write_alias: bool = True,
        id_field: str | None = ID_FIELD_DEFAULT,
        raise_on_error: bool = False,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        return await super().bulk_delete(
            documents=[d.model_dump() for d in documents],
            operation_type=OperationType.DELETE,
            base_alias=base_alias,
            use_write_alias=use_write_alias,
            id_field=id_field,
            raise_on_error=raise_on_error,
            **kwargs,
        )
