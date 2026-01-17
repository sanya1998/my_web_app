# TODO: внимательнее эти моменты проработать:
#  при реиндексе надежнее использовать index и для create, и для update.
#  при реиндексе удаление может не произойти ни в одном из индексов, так как возникает ошибка отсутствия документа
#  при записи всегда два запроса (получение индексов по алиасу, запись)
#  при реиндексе два запроса для записи в разные индексы (а можно bulk)
import asyncio
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Type

from app.config.common import settings
from elastic_transport import ApiResponse
from elasticsearch.dsl import AsyncDocument, AsyncSearch
from elasticsearch.dsl.query import Term
from es.clients.base import BaseESClient
from es.clients.models.aliases import AddAlias, AddAliasInfo, AliasInfo, RemoveAlias
from es.clients.models.reindex_history import ReindexHistory


class IndexESClient(BaseESClient):
    """
    Управление созданием и миграцией индексов

    Правила:

    1. Каждый индекс должен иметь 3 алиаса, например для products_v1:
    ├── products          (базовый алиас)     → читает пользователь
    ├── products_read     (read алиас)        → читает приложение
    └── products_write    (write алиас)       → пишет приложение

    2. Для каждого индекса создается DSL модель в es/dsl/indices/:
    ```python
    # es/dsl/indices/products.py
    from elasticsearch.dsl import Document

    class ProductDocument(Document):
        # поля документа

        class Index:
            name = "products_v3"  # Имя индекса с версией
            settings = {...}      # Настройки индекса
    ```

    3. АЛГОРИТМЫ МИГРАЦИИ
        🔹 Сценарий 1: Первое создание индекса
            1. Создать DSL модель в es/dsl/indices/
            2. Выполнить скрипт `python3 create_index.py`

        🔹 Сценарий 2: Миграция и отслеживание (Во время реиндекса: чтение из старого индекса, запись в оба индекса)
            1. Обновить DSL модель (увеличить версию в имени индекса)
            2. Выполнить скрипт `python3 reindex_smartly.py start_reindex`
            3. Выполнить скрипт `python3 reindex_smartly.py end_reindex`
    """

    def __init__(
        self,
        hosts: Optional[List[str]] = None,
        **kwargs,
    ):
        """
        Инициализация клиента для управления индексами

        Args:
            hosts: Список URL нод Elasticsearch (например: ["http://localhost:9200"])
            **kwargs: Дополнительные параметры для AsyncElasticsearch
        """
        super().__init__(hosts=hosts, default_alias=settings.ES_HISTORY_BASE_ALIAS, **kwargs)

    async def _create_new_index(self, document_class: Type[AsyncDocument]) -> str:
        """
        Создать новый индекс на основе DSL модели

        Создает индекс с именем {base_alias}_v{version}, где version берется из
        DSL модели в es/dsl/indices/{base_alias}.py.

        Процесс:
        1. Загружает конфигурацию из DSL модели
        2. Проверяет, не существует ли уже индекс с таким именем
        3. Создает индекс с настройками и маппингами из конфигурации
        4. Возвращает имя созданного индекса

        Args:
            base_alias: Базовый алиас (имя DSL модели)

        Returns:
            Имя созданного индекса (например, "products_v3")

        Raises:
            ValueError: если индекс с таким именем уже существует
            ValueError: если DSL модель не найдена

        Пример:
            ```python
            # Создание индекса products_v3 на основе es/dsl/indices/products.py
            index_name = await index_client._create_new_index("products")
            print(f"Создан индекс: {index_name}")
            ```
        """
        # TODO: проверить нет ли общего с create_first_index
        index_name = document_class.Index.name

        if await self.indices.exists(index=index_name):
            raise ValueError(f"Index '{index_name}'elasticsearch already exists")

        await document_class.init(using=self)

        return index_name

    async def _add_all_aliases(self, index_name: str, base_alias: str) -> None:
        """
        Добавить все три алиаса к индексу

        Атомарно добавляет базовый алиас, read алиас и write алиас к указанному индексу.
        Используется при первоначальном создании индекса.

        Добавляемые алиасы:
        - {base_alias}          (базовый алиас для чтения пользователем)
        - {base_alias}_read     (read алиас для чтения приложением)
        - {base_alias}_write    (write алиас для записи приложением)

        Args:
            index_name: Имя индекса, к которому добавляются алиасы (например, "products_v3")
            base_alias: Базовый алиас (например, "products")

        Пример:
            ```python
            # После создания индекса products_v3 добавляем все алиасы
            await index_client._add_all_aliases(
                index_name="products_v3",
                base_alias="products"
            )
            # Теперь доступны:
            # - products → products_v3
            # - products_read → products_v3
            # - products_write → products_v3
            ```
        """
        actions = [
            AddAlias(AddAliasInfo(index=index_name, alias=base_alias)),
            AddAlias(AddAliasInfo(index=index_name, alias=self._get_read_alias(base_alias))),
            AddAlias(AddAliasInfo(index=index_name, alias=self._get_write_alias(base_alias))),
        ]
        await self._setup_aliases(*actions)

    async def _add_write_alias_only(self, index_name: str, base_alias: str) -> None:
        """
        Добавить только write алиас к индексу

        Добавляет только write алиас к указанному индексу, оставляя базовый
        и read алиасы pointing на старый индекс. Используется во время миграции
        для реализации двойной записи.

        Сценарий использования:
        1. Во время реиндексации нужно писать в оба индекса (старый и новый)
        2. Добавляем write алиас на новый индекс
        3. Приложение продолжает писать через write алиас, который теперь указывает на оба индекса
        4. Чтение идет со старого индекса через базовый/read алиасы

        Args:
            index_name: Имя индекса, к которому добавляется write алиас
            base_alias: Базовый алиас

        Пример:
            ```python
            # Во время миграции с products_v2 на products_v3
            # Добавляем write алиас на новый индекс для двойной записи
            await index_client._add_write_alias_only(
                index_name="products_v3",
                base_alias="products"
            )
            # Теперь:
            # - products_write → products_v2, products_v3 (двойная запись)
            # - products, products_read → products_v2 (чтение со старого)
            ```
        """
        action = AddAlias(AddAliasInfo(index=index_name, alias=self._get_write_alias(base_alias)))
        await self._setup_aliases(action)

    async def _switch_aliases(self, old_index: str, new_index: str, base_alias: str) -> None:
        """
        Атомарно переключить алиасы со старого индекса на новый

        Выполняет атомарное переключение всех алиасов в одной операции.
        Используется в конце миграции для переключения трафика на новый индекс.

        Операции выполняемые атомарно:
        1. Удаление с old_index:
           - {base_alias}
           - {base_alias}_read
           - {base_alias}_write
        2. Добавление к new_index:
           - {base_alias}
           - {base_alias}_read
           - write алиас уже должен быть добавлен через `_add_write_alias_only()`

        Требования:
        - new_index уже должен иметь write алиас (добавлен через `_add_write_alias_only()`)
        - old_index должен иметь все три алиаса
        - Операция атомарна: либо все изменения применяются, либо ни одно

        Args:
            old_index: Старый индекс, с которого удаляются алиасы
            new_index: Новый индекс, на который добавляются алиасы
            base_alias: Базовый алиас

        Пример:
            ```python
            # Завершение миграции: переключаем алиасы с products_v2 на products_v3
            await index_client._switch_aliases(
                old_index="products_v2",
                new_index="products_v3",
                base_alias="products"
            )
            # Теперь:
            # - products, products_read, products_write → products_v3
            # - products_v2 больше не имеет алиасов
            ```
        """
        read_alias = self._get_read_alias(base_alias)
        write_alias = self._get_write_alias(base_alias)

        actions = [
            RemoveAlias(AliasInfo(index=old_index, alias=base_alias)),
            RemoveAlias(AliasInfo(index=old_index, alias=read_alias)),
            RemoveAlias(AliasInfo(index=old_index, alias=write_alias)),
            AddAlias(AddAliasInfo(index=new_index, alias=base_alias)),
            AddAlias(AddAliasInfo(index=new_index, alias=read_alias)),
        ]

        await self._setup_aliases(*actions)

    async def _start_reindex(
        self,
        source_index: str,
        dest_index: str,
        **kwargs,
    ) -> str:
        """
        Запустить асинхронный реиндекс

        Запускает операцию reindex в асинхронном режиме (wait_for_completion=False)
        и возвращает ID задачи для отслеживания прогресса.

        Процесс:
        1. Запускает Elasticsearch reindex API с wait_for_completion=False
        2. Получает task_id из ответа Elasticsearch
        3. Возвращает task_id для последующего отслеживания

        Args:
            source_index: Исходный индекс (откуда копируются документы)
            dest_index: Целевой индекс (куда копируются документы)
            **kwargs: Дополнительные параметры Elasticsearch reindex API:
                - wait_for_completion: bool - всегда False в этом методе
                - refresh: bool - обновить целевой индекс после завершения
                - timeout: str - таймаут операции ("30s", "1m")
                - requests_per_second: int - ограничение скорости (документов/сек)
                - slices: int | str - количество срезов для параллельной обработки
                - max_docs: int - максимальное количество документов для копирования
                - script: Dict - Painless script для трансформации документов
                - И другие параметры Elasticsearch reindex API

        Returns:
            task_id: ID задачи Elasticsearch для отслеживания прогресса

        Пример:
            ```python
            # Запуск реиндекса с параллельной обработкой
            task_id = await index_client._start_reindex(
                source_index="products_v2",
                dest_index="products_v3",
                slices="auto",  # Автоматическое определение количества срезов
                requests_per_second=1000,  # Ограничение скорости
                refresh=False  # Не обновлять сразу
            )
            print(f"Запущен реиндекс, task_id: {task_id}")
            ```
        """
        response = await self.reindex(
            source=dict(index=source_index),
            dest=dict(index=dest_index),
            wait_for_completion=False,
            **kwargs,
        )
        task_id = response.get("task")
        return task_id

    async def _write_task_id(self, base_alias: str, task_id: str, source_index: str, dest_index: str) -> None:
        """
        Записать информацию о задаче реиндекса в индекс истории

        Сохраняет метаинформацию о запущенной задаче реиндекса в специальный индекс
        settings.ES_HISTORY_BASE_ALIAS (например `reindex_history`) для последующего отслеживания и восстановления.

        Сохраняемая информация:
        - task_id - идентификатор задачи Elasticsearch
        - base_alias - базовый алиас, для которого выполняется реиндекс
        - source_index - исходный индекс (старая версия)
        - dest_index - целевой индекс (новая версия)
        - started_at - время начала реиндекса

        Args:
            task_id: ID задачи реиндекса из Elasticsearch
            base_alias: Базовый алиас, для которого выполняется реиндекс
            source_index: Исходный индекс (старая версия)
            dest_index: Целевой индекс (новая версия)

        Пример:
            ```python
            # После запуска реиндекса сохраняем информацию
            await index_client._write_task_id(
                task_id="abc123:456",
                base_alias="products",
                source_index="products_v2",
                dest_index="products_v3"
            )
            ```
        """
        history_doc = ReindexHistory(
            task_id=task_id,
            base_alias=base_alias,
            dest_index=dest_index,
            source_index=source_index,
            started_at=datetime.utcnow(),
        )

        if not await self._get_index_by_alias(self._default_alias):
            await self.create_first_index(self._default_alias)

        await self.index(document=history_doc.model_dump())

    async def get_task_silent(
        self,
        *,
        task_id: str,
        **kwargs,
    ) -> ApiResponse:
        """
        Упрощённая версия tasks.get() без предупреждений о technical preview

        Args:
            task_id: ID задачи (обязательный)
            **kwargs: Дополнительные параметры Elasticsearch API:
                wait_for_completion: t.Optional[bool] = None
                timeout: t.Optional[t.Union[str, t.Literal[-1], t.Literal[0]]] = None
                error_trace: t.Optional[bool] = None
                filter_path: t.Optional[t.Union[str, t.Sequence[str]]] = None
                human: t.Optional[bool] = None
                pretty: t.Optional[bool] = None
        """
        return await self.perform_request(
            "GET",
            f"/_tasks/{task_id}",
            params=kwargs,
            headers={"accept": "application/json"},
        )

    async def _wait_reindex(
        self,
        base_alias: str,
        check_interval: int = 10,
    ) -> ReindexHistory:
        """
        Ожидать завершения реиндекса

        Мониторит прогресс задачи реиндекса и ожидает ее завершения.
        Выводит информацию о прогрессе в консоль.

        Логика работы:
            1. Найти в _reindex_history последний документ по base_alias
            2. Взять task_id
            3. Проверить статус через tasks.get(task_id)
            4. Циклически проверять до завершения

        Args:
            base_alias: базовый алиас
            check_interval: интервал проверки в секундах

        Returns:
            Документ истории реиндекса с информацией о задаче
        """
        # Найти историю реиндекса
        search_query = AsyncSearch()[:1].query(Term(base_alias=base_alias)).sort("-started_at")
        response = await self.search(body=search_query.to_dict())

        if not response["hits"]["hits"]:
            raise ValueError(f"No reindex history found for base_alias: {base_alias}")

        history_doc = response["hits"]["hits"][0]["_source"]
        task_id = history_doc["task_id"]

        while True:
            response = await self.get_task_silent(task_id=task_id)
            task_body = response.body

            task_info = task_body.get("task", {})
            if task_body.get("completed"):
                print("Reindex completed successfully")
                break

            task_status = task_info.get("status", {})
            response_data = task_body.get("response", {})

            if (total := task_status.get("total", 0)) == 0:
                await asyncio.sleep(check_interval)
                continue

            created = task_status.get("created", 0)
            updated = task_status.get("updated", 0)
            deleted = task_status.get("deleted", 0)
            processed = created + updated + deleted

            failures = len(response_data.get("failures", []))
            took_ms = response_data.get("took", 0)
            progress = int((processed / total) * 100) if total > 0 else 0

            timestamp = datetime.utcnow()
            print(
                f"{timestamp}: Reindex progress: {progress}% "
                f"({processed}/{total} docs processed : "
                f"{created} created, {updated} updated, {deleted} deleted), "
                f"{failures} failures, {took_ms}ms"
            )

            await asyncio.sleep(check_interval)

        return ReindexHistory(**history_doc)

    # === ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ===

    async def _setup_aliases(self, *actions: AddAlias | RemoveAlias) -> None:
        """Настроить алиасы"""
        await self.indices.update_aliases(actions=[asdict(a) for a in actions])

    async def _get_index_by_alias(self, base_alias: str) -> Optional[str]:
        """
        Получить индекс по базовому алиасу
        Правило: base_alias всегда указывает только на один индекс
        """
        indices = await self.get_indices_by_alias(base_alias)
        return indices[0] if indices else None

    async def create_first_index(self, document_class: Type[AsyncDocument]) -> str:
        """
        Создать первый индекс для базового алиаса

        Полный процесс создания индекса с нуля:
        1. Создает новый индекс на основе DSL модели
        2. Добавляет все три алиаса (базовый, _read, _write) к созданному индексу
        3. Возвращает имя созданного индекса

        Используется при первоначальном развертывании приложения или при
        создании нового типа документов.

        Args:
            document_class: TODO

        Returns:
            Имя созданного индекса (например, "products_v3")

        Raises:
            ValueError: если индекс уже существует
            ValueError: если DSL модель не найдена

        Пример использования через скрипт:
            ```python
            # create_index.py
            async with IndexClient(hosts=settings.ES_HOSTS) as client:
                index_name = await client.create_first_index("products")
                print(f"Создан индекс: {index_name}")
            ```

        После выполнения:
            - Создан индекс: products_v3
            - Алиасы: products → products_v3, products_read → products_v3, products_write → products_v3
            - Индекс готов к использованию через клиенты BaseESClient/PydanticESClient
        """
        index_name = document_class.Index.name

        if await self.indices.exists(index=index_name):
            raise ValueError(f"Index '{index_name}' already exists")

        await document_class.init(using=self)

        base_alias = index_name.rsplit("_v", 1)[0]
        await self._add_all_aliases(index_name, base_alias)

        return index_name

    async def start_reindex(
        self,
        document_class: Type[AsyncDocument],
        **reindex_kwargs,
    ):
        """
        Начать процесс миграции индекса (реиндексации)

        Запускает процесс миграции на новую версию индекса. Используется при
        изменении маппингов, настроек или необходимости переиндексации данных.

        Процесс миграции (zero-downtime):
        1. Создает новый индекс на основе обновленной DSL модели
        2. Добавляет write алиас на новый индекс (двойная запись)
        3. Запускает асинхронный реиндекс данных со старого индекса на новый
        4. Сохраняет информацию о задаче в индекс истории

        Args:
            document_class: TODO

        Returns:
            task_id: ID задачи реиндекса для отслеживания прогресса

        Пример использования через скрипт:
            ```bash
            # Обновить es/dsl/indices/products.py (увеличить version в имени индекса)
            # Запустить реиндекс
            python3 reindex_smartly.py start_reindex
            ```

        Состояние системы после выполнения:
            - Новый индекс: products_v3 (на основе обновленной DSL модели)
            - Старый индекс: products_v2 (остается для чтения)
            - Алиасы:
              * products, products_read → products_v2 (чтение со старого)
              * products_write → products_v2, products_v3 (двойная запись в оба)
            - Запущен фоновый процесс копирования данных products_v2 → products_v3
        """
        new_index_name = await self._create_new_index(document_class)
        base_alias = new_index_name.rsplit("_v", 1)[0]

        old_index = await self._get_index_by_alias(base_alias)
        if not old_index:
            raise ValueError(f"No existing index found for base_alias: {base_alias}")

        await self._add_write_alias_only(index_name=new_index_name, base_alias=base_alias)

        task_id = await self._start_reindex(source_index=old_index, dest_index=new_index_name, **reindex_kwargs)

        await self._write_task_id(
            task_id=task_id, base_alias=base_alias, source_index=old_index, dest_index=new_index_name
        )

        return task_id

    async def end_reindex(self, document_class: Type[AsyncDocument], check_interval: int = 10):
        """
        Завершить процесс миграции индекса

        Завершает миграцию, переключая все алиасы на новый индекс
        после успешного завершения реиндексации.

        Процесс завершения:
        1. Ожидает завершения задачи реиндекса (мониторинг прогресса)
        2. Атомарно переключает все алиасы с старого индекса на новый
        3. Удаляет алиасы со старого индекса

        Args:
            document_class: TODO
            check_interval: Интервал проверки прогресса в секундах

        Пример использования через скрипт:
            ```bash
            # Дождаться завершения реиндекса и переключить алиасы
            python3 reindex_smartly.py end_reindex
            ```

        Состояние системы после выполнения:
            - Новый индекс: products_v3 (полностью заполнен и актуален)
            - Старый индекс: products_v2 (больше не имеет алиасов)
            - Алиасы:
              * products, products_read, products_write → products_v3
            - Приложение читает и пишет только в новый индекс
        """
        new_index_name = document_class.Index.name
        base_alias = new_index_name.rsplit("_v", 1)[0]

        old_index = await self._get_index_by_alias(base_alias)
        if not old_index:
            raise ValueError(f"No existing index found for base_alias: {base_alias}")

        task = await self._wait_reindex(base_alias=base_alias, check_interval=check_interval)

        if task.dest_index != new_index_name:
            raise ValueError(f"Destination index mismatch. Expected: {new_index_name}, Got: {task.dest_index}")

        await self._switch_aliases(old_index=old_index, new_index=new_index_name, base_alias=base_alias)

    async def delete_index(
        self,
        document_class: Type[AsyncDocument],
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Удалить индекс по DSL модели

        Args:
            document_class: Класс документа Elasticsearch DSL
            **kwargs: Дополнительные параметры Elasticsearch delete index API:
                - timeout: str - таймаут операции ("30s", "1m")
                - master_timeout: str - таймаут ожидания master-ноды
                - ignore_unavailable: bool - игнорировать отсутствующие индексы
                - allow_no_indices: bool - разрешить если индекс не существует
                - expand_wildcards: str | List[str] - обработка wildcard
                - wait_for_active_shards: str - ждать активных шардов

        Returns:
            Ответ Elasticsearch с подтверждением удаления

        Пример:
            ```python
            from es.dsl.indices.products import ProductDocument
            await client.delete_index(ProductDocument)
            ```
        """
        index_name = document_class.Index.name

        # Проверяем существование
        if not await self.indices.exists(index=index_name):
            return {"message": f"Index '{index_name}' did not exist"}

        # Удаляем
        return await self.indices.delete(index=index_name, **kwargs)
