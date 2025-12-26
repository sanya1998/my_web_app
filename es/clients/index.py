# TODO: внимательнее эти моменты проработать:
#  при реиндексе надежнее использовать index и для create, и для update.
#  при реиндексе удаление не происходит ни в одном из индексов, так как возникает ошибка отсутствия документа
import asyncio
from dataclasses import asdict
from datetime import datetime
from typing import List, Optional

import yaml
from app.common.logger import logger
from app.config.common import settings
from elastic_transport import ApiResponse
from es.clients.base import BaseESClient
from es.clients.models.aliases import AddAlias, AddAliasInfo, AliasInfo, RemoveAlias
from es.clients.models.config import IndexConfig
from es.clients.models.reindex_history import ReindexHistory
from es.main_query.main import MainQuery
from es.main_query.query import Term


class IndexClient(BaseESClient):
    """
    Управление созданием и миграцией индексов

    Правила:

    1. Каждый индекс должен иметь 3 алиаса, например для products_v1:
    ├── products          (базовый алиас)     → читает пользователь
    ├── products_read     (read алиас)        → читает приложение
    └── products_write    (write алиас)       → пишет приложение

    2. Перед созданием индекса или реиндексом нужно создать или изменить файл es/indices/{base_alias}.yaml:
    ```yaml
    version: "2"                     # Версия индекса
    settings:                        # Настройки индекса
      number_of_shards: 3
      number_of_replicas: 1
    mappings:                        # Маппинги полей
      properties:
        field_name:
          type: "text"
    ```

    3. АЛГОРИТМЫ МИГРАЦИИ
        🔹 Сценарий 1: Первое создание индекса
            1. Создать файл конфигурации es/indices/products.yaml
            2. Выполнить скрипт `python3 create_index.py`

        🔹 Сценарий 2: Миграция и отслеживание (Во время реиндекса: чтение из старого индекса, запись в оба индекса)
            1. Обновить es/indices/products.yaml
            2. Выполнить скрипт `python3 reindex_smartly.py start_reindex`
            3. Выполнить скрипт `python3 reindex_smartly.py end_reindex`
    """

    def __init__(
        self,
        hosts: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(hosts=hosts, default_alias="reindex_history", **kwargs)

    @staticmethod
    def _load_index_config(
        base_alias: str,
        directory: str = settings.ES_INDICES_DIRECTORY,
        file_extension: str = settings.ES_INDEX_FILE_EXTENSION,
    ) -> IndexConfig:
        """Загрузить конфигурацию индекса"""
        config_path = f"{directory}/{base_alias}.{file_extension}"

        with open(config_path, "r", encoding=settings.ES_INDEX_FILE_ENCODING) as f:
            raw_config = yaml.safe_load(f)

        return IndexConfig(base_alias=base_alias, **raw_config)

    async def _create_new_index(
        self,
        base_alias: str,
        directory: str = settings.ES_INDICES_DIRECTORY,
        file_extension: str = settings.ES_INDEX_FILE_EXTENSION,
    ) -> str:
        """
        Создать новый индекс на основе YAML-конфигурации

        Создает индекс с именем {base_alias}_v{version}, где version берется из
        YAML-конфигурационного файла.

        Процесс:
        1. Загружает конфигурацию из es/indices/{base_alias}.yaml
        2. Проверяет, не существует ли уже индекс с таким именем
        3. Создает индекс с настройками и маппингами из конфигурации
        4. Возвращает имя созданного индекса

        Args:
            base_alias: Базовый алиас (имя YAML-файла без расширения)
            directory: Директория с конфигурационными файлами (по умолчанию: settings.ES_INDICES_DIRECTORY)
            file_extension: Расширение конфигурационных файлов (по умолчанию: settings.ES_INDEX_FILE_EXTENSION)

        Returns:
            Имя созданного индекса (например, "products_v2")

        Raises:
            ValueError: если индекс с таким именем уже существует
            FileNotFoundError: если конфигурационный файл не найден
            yaml.YAMLError: если ошибка парсинга YAML

        Пример:
            ```python
            # Создание индекса products_v2 на основе es/indices/products.yaml
            index_name = await index_client._create_new_index("products")
            print(f"Создан индекс: {index_name}")

            # С кастомной директорией конфигов
            index_name = await index_client._create_new_index(
                base_alias="users",
                directory="/path/to/configs",
                file_extension="yml"
            )
            ```

        См. также:
            - `IndexConfig` - модель конфигурации индекса
            - `create_first_index()` - публичный метод для создания первого индекса
        """
        config = self._load_index_config(base_alias=base_alias, directory=directory, file_extension=file_extension)
        new_index_name = f"{config.base_alias}_v{config.version}"

        if config.settings is None:
            logger.info(f"Index {new_index_name}: using default settings")
        if config.mappings is None:
            logger.warning(f"Index {new_index_name}: no mappings defined - dynamic mapping enabled")

        if await self.indices.exists(index=new_index_name):
            raise ValueError(f"Index '{new_index_name}' already exists")

        await self.indices.create(index=new_index_name, settings=config.settings, mappings=config.mappings)
        return new_index_name

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
            index_name: Имя индекса, к которому добавляются алиасы (например, "products_v2")
            base_alias: Базовый алиас (например, "products")

        Пример:
            ```python
            # После создания индекса products_v2 добавляем все алиасы
            await index_client._add_all_aliases(
                index_name="products_v2",
                base_alias="products"
            )
            # Теперь доступны:
            # - products → products_v2
            # - products_read → products_v2
            # - products_write → products_v2
            ```

        Примечание:
            - Использует атомарную операцию update_aliases
            - Все три алиаса добавляются за одну операцию
            - Для добавления только write алиаса используйте `_add_write_alias_only()`
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
            # Во время миграции с products_v1 на products_v2
            # Добавляем write алиас на новый индекс для двойной записи
            await index_client._add_write_alias_only(
                index_name="products_v2",
                base_alias="products"
            )
            # Теперь:
            # - products_write → products_v1, products_v2 (двойная запись)
            # - products, products_read → products_v1 (чтение со старого)
            ```

        Примечание:
            - Используется в `start_reindex()` для настройки двойной записи
            - После завершения миграции алиасы переключаются через `_switch_aliases()`
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
            # Завершение миграции: переключаем алиасы с products_v1 на products_v2
            await index_client._switch_aliases(
                old_index="products_v1",
                new_index="products_v2",
                base_alias="products"
            )
            # Теперь:
            # - products, products_read, products_write → products_v2
            # - products_v1 больше не имеет алиасов
            ```

        Примечание:
            - Атомарность гарантирует отсутствие downtime
            - Вызывается в `end_reindex()` после завершения реиндексации
            - Старый индекс можно удалить после проверки работы нового
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
                source_index="products_v1",
                dest_index="products_v2",
                slices="auto",  # Автоматическое определение количества срезов
                requests_per_second=1000,  # Ограничение скорости
                refresh=False  # Не обновлять сразу
            )

            print(f"Запущен реиндекс, task_id: {task_id}")
            # task_id имеет формат: "node_id:task_number"
            ```

        Примечание:
            - Для отслеживания прогресса используйте `_wait_reindex()` или `get_task_silent()`
            - Реиндекс выполняется асинхронно, метод возвращает управление сразу
            - Используется в `start_reindex()` для запуска миграции
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
        `reindex_history` для последующего отслеживания и восстановления.

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
                source_index="products_v1",
                dest_index="products_v2"
            )

            # Теперь в индексе reindex_history есть запись:
            # {
            #   "task_id": "abc123:456",
            #   "base_alias": "products",
            #   "source_index": "products_v1",
            #   "dest_index": "products_v2",
            #   "started_at": "2024-01-15T10:30:00Z"
            # }
            ```

        Примечание:
            - Если индекс `reindex_history` не существует, он создается автоматически
            - Используется в `start_reindex()` для сохранения состояния
            - `_wait_reindex()` читает из этого индекса для отслеживания прогресса
            - Документ индексируется с авто-генерируемым ID
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

        await self.index(document=history_doc.model_dump())  # TODO: refresh index

    async def get_task_silent(
        self,
        *,
        task_id: str,
        **kwargs,
    ) -> ApiResponse:
        """
        Упрощённая версия tasks.get() без предупреждений о technical preview.

        Args:
            task_id: ID задачи (обязательный)
            **kwargs: Дополнительные параметры Elasticsearch API:

                wait_for_completion: t.Optional[bool] = None
                    Если True, запрос блокируется до завершения задачи.

                timeout: t.Optional[t.Union[str, t.Literal[-1], t.Literal[0]]] = None
                    Время ожидания ответа. Если ответ не получен до истечения таймаута,
                    запрос завершается ошибкой.
                    Формат: "30s", "1m", "500ms"
                    Специальные значения: -1 (бесконечно), 0 (без ожидания)

                error_trace: t.Optional[bool] = None
                    Если True, включает трассировку стека в ответе при ошибках.

                filter_path: t.Optional[t.Union[str, t.Sequence[str]]] = None
                    Фильтрация полей в ответе. Например: "task.status,task.description"

                human: t.Optional[bool] = None
                    Если True, возвращает время и размеры в удобочитаемом формате.
                    Например: "1h" вместо "3600s"

                pretty: t.Optional[bool] = None
                    Если True, возвращает "красивый" (отформатированный) JSON.

                Также принимает любые другие допустимые query-параметры Elasticsearch Tasks API.

        Returns:
            ObjectApiResponse с телом ответа Elasticsearch.
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
        Получить статус реиндекса

        Args:
            base_alias: базовый алиас
            check_interval: интервал проверки в секундах

        Returns:
            {
                "task_id": "abc123:456",
                "status": "running",  # "running", "completed", "failed"
                "source_index": "products_v1",
                "dest_index": "products_v2"
            }

        Logic:
            1. Найти в _reindex_history последний документ по base_alias
            2. Взять task_id
            3. Проверить статус через tasks.get(task_id)
            4. Циклически проверять до завершения
        """
        # Найти историю реиндекса
        search_query = MainQuery(
            query=Term(field="base_alias", value=base_alias), sort=[{"started_at": {"order": "desc"}}], size=1
        )
        response = await self.search(body=search_query())

        if not response["hits"]["hits"]:
            raise ValueError(f"No reindex history found for base_alias: {base_alias}")

        history_doc = response["hits"]["hits"][0]["_source"]
        task_id = history_doc["task_id"]

        while True:
            response = await self.get_task_silent(task_id=task_id)
            task_body = response.body

            # Получаем статус задачи
            task_info = task_body.get("task", {})
            task_status = task_info.get("status", {})
            response_data = task_body.get("response", {})

            # Проверяем, есть ли общее количество документов
            if (total := task_status.get("total", 0)) == 0:
                # Если total=0, возможно задача ещё не начала обрабатывать документы
                await asyncio.sleep(check_interval)
                continue

            # Вычисляем прогресс
            created = task_status.get("created", 0)
            updated = task_status.get("updated", 0)
            deleted = task_status.get("deleted", 0)
            processed = created + updated + deleted

            # Статистика выполнения
            failures = len(response_data.get("failures", []))
            took_ms = response_data.get("took", 0)
            progress = int((processed / total) * 100) if total > 0 else 0

            # Выводим информацию о прогрессе
            timestamp = datetime.utcnow()
            print(
                f"{timestamp}: Reindex progress: {progress}% "
                f"({processed}/{total} docs processed : "
                f"{created} created, {updated} updated, {deleted} deleted), "
                f"{failures} failures, {took_ms}ms"
            )

            # Проверяем завершение задачи
            if task_body.get("completed"):
                print(f"{timestamp}: Reindex completed successfully")
                break

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
        indices = await self._get_indices_by_alias(base_alias)
        return indices[0] if indices else None

    async def create_first_index(
        self,
        base_alias: str,
        directory: str = settings.ES_INDICES_DIRECTORY,
        file_extension: str = settings.ES_INDEX_FILE_EXTENSION,
    ) -> str:
        """
        Создать первый индекс для базового алиаса

        Полный процесс создания индекса с нуля:
        1. Создает новый индекс на основе YAML-конфигурации
        2. Добавляет все три алиаса (базовый, _read, _write) к созданному индексу
        3. Возвращает имя созданного индекса

        Используется при первоначальном развертывании приложения или при
        создании нового типа документов.

        Args:
            base_alias: Базовый алиас для индекса (например, "products")
            directory: Директория с конфигурационными файлами
            file_extension: Расширение конфигурационных файлов

        Returns:
            Имя созданного индекса (например, "products_v1")

        Raises:
            ValueError: если индекс уже существует
            FileNotFoundError: если конфигурационный файл не найден

        Пример использования через скрипт:
            ```python
            # create_index.py
            async with IndexClient(hosts=settings.ES_HOSTS) as client:
                index_name = await client.create_first_index("products")
                print(f"Создан индекс: {index_name}")
            ```

        Пример конфигурационного файла (es/indices/products.yaml):
            ```yaml
            version: "1"
            settings:
              number_of_shards: 3
              number_of_replicas: 1
            mappings:
              properties:
                name: {type: text}
                price: {type: float}
            ```

        После выполнения:
            - Создан индекс: products_v1
            - Алиасы: products → products_v1, products_read → products_v1, products_write → products_v1
            - Индекс готов к использованию через клиенты BaseESClient/PydanticESClient
        """
        index = await self._create_new_index(base_alias=base_alias, directory=directory, file_extension=file_extension)
        await self._add_all_aliases(index, base_alias)
        print(f"Created index: {index}")
        return index

    async def start_reindex(
        self,
        base_alias: str,
        directory: str = settings.ES_INDICES_DIRECTORY,
        file_extension: str = settings.ES_INDEX_FILE_EXTENSION,
    ):
        """
        Начать процесс миграции индекса (реиндексации)

        Запускает процесс миграции на новую версию индекса. Используется при
        изменении маппингов, настроек или необходимости переиндексации данных.

        Процесс миграции (zero-downtime):
        1. Создает новый индекс на основе обновленной конфигурации
        2. Добавляет write алиас на новый индекс (двойная запись)
        3. Запускает асинхронный реиндекс данных со старого индекса на новый
        4. Сохраняет информацию о задаче в индекс истории

        Args:
            base_alias: Базовый алиас для миграции (например, "products")
            directory: Директория с конфигурационными файлами
            file_extension: Расширение конфигурационных файлов

        Returns:
            task_id: ID задачи реиндекса для отслеживания прогресса

        Пример использования через скрипт:
            ```bash
            # Обновить es/indices/products.yaml (увеличить version)
            # Запустить реиндекс
            python3 reindex_smartly.py start_reindex
            ```

        Состояние системы после выполнения:
            - Новый индекс: products_v2 (на основе обновленной конфигурации)
            - Старый индекс: products_v1 (остается для чтения)
            - Алиасы:
              * products, products_read → products_v1 (чтение со старого)
              * products_write → products_v1, products_v2 (двойная запись в оба)
            - Запущен фоновый процесс копирования данных products_v1 → products_v2

        Примечание:
            - Во время миграции приложение продолжает работать без downtime
            - Чтение идет со старого индекса, запись идет в оба индекса
            - Для завершения миграции выполните `end_reindex()`
        """
        new_i = await self._create_new_index(base_alias=base_alias, directory=directory, file_extension=file_extension)
        await self._add_write_alias_only(index_name=new_i, base_alias=base_alias)
        old_i = await self._get_index_by_alias(base_alias)
        task_id = await self._start_reindex(source_index=old_i, dest_index=new_i)
        await self._write_task_id(task_id=task_id, base_alias=base_alias, source_index=old_i, dest_index=new_i)
        return task_id

    async def end_reindex(self, base_alias: str, check_interval: int = 10):
        """
        Завершить процесс миграции индекса

        Завершает миграцию, переключая все алиасы на новый индекс
        после успешного завершения реиндексации.

        Процесс завершения:
        1. Ожидает завершения задачи реиндекса (мониторинг прогресса)
        2. Атомарно переключает все алиасы с старого индекса на новый
        3. Удаляет алиасы со старого индекса

        Args:
            base_alias: Базовый алиас для завершения миграции
            check_interval: Интервал проверки прогресса в секундах

        Пример использования через скрипт:
            ```bash
            # Дождаться завершения реиндекса и переключить алиасы
            python3 reindex_smartly.py end_reindex
            ```

        Состояние системы после выполнения:
            - Новый индекс: products_v2 (полностью заполнен и актуален)
            - Старый индекс: products_v1 (больше не имеет алиасов)
            - Алиасы:
              * products, products_read, products_write → products_v2
            - Приложение читает и пишет только в новый индекс

        Что делать дальше:
            - Проверить корректность работы приложения с новым индексом
            - Удалить старый индекс products_v1 (если больше не нужен):
              ```python
              await client.indices.delete(index="products_v1")
              ```
            - Обновить конфигурацию при необходимости

        Примечание:
            - Переключение алиасов атомарно (zero-downtime)
            - Старый индекс остается доступным для отката при проблемах
            - Рекомендуется выполнять в период низкой нагрузки
        """
        old_i = await self._get_index_by_alias(base_alias)
        task = await self._wait_reindex(base_alias=base_alias, check_interval=check_interval)
        new_i = task.dest_index
        await self._switch_aliases(old_index=old_i, new_index=new_i, base_alias=base_alias)
