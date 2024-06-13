Запуск сервисов локально:

`make up-services`

Выполнить миграции на локальную базу данных:

`make forward_migrations_head_local`

Первый Debug в PyCharm:
1. Создать новую конфигурацию для Python
2. Выбрать интерпретатор Python
3. Указать путь до скрипта `manage.py`
4. Добавить аргумент (для runserver: "runserver"; для run_consumer: "run-consumer")
5. Указать рабочую директорию - корень проекта
6. Указать путь до одного из .env-файлов в директории `.envs/`
7. Запустить Debug

Некоторые команды из Makefile не запускаются через конфигурацию Makefile, т.к. там не подключается виртуальное окружение.
Запуск таких команд из Makefile в PyCharm:
1. Создать конфигурацию для Shell Script
2. Выбрать Script Text
3. Ввести команду в текстовое поле, например `make alembic_upgrade_head`
4. Выполнить конфигурацию

Запретить отслеживать изменения в .env-файлах. 

`git update-index --assume-unchanged .envs/*`

Проект разрабатывается с помощью курса https://stepik.org/course/153849/promo

TODO:
1) Посмотреть все TODO в коде
2) К бд сделать подключению через `@app.on_event("startup")` и сразу создавать пул (или оставить то, как сейчас?)
3) Проверять подключение к бд при старте приложения (Lifespan)
2) Все миграции откатить до начала и готовую бд сделать первой ревизией
`alembic revision --autogenerate -m "Initial migration"`
3) создать example.env (?)
4) придумать что-нибудь с submodule (например, модели) и со своей библиотекой
5) Использовать Lifespan (fast api) (Добавить какого-нибудь клиента)
6) Перейти на SQLModel 
7) Поля в фильтрах отелей
9) id: uuid.UUID
10) Попробовать autoflake8
11) pre-commit
13) Разобраться с енвами для бд (число пулов и тд)
15) Написать свой json сериалайзер, чтоб не делать json.loads(json.dumps(
16) Ошибки писать в логи (подробно, с трейсом)
17) Сериализация исключений. Что-то про респонс-модел
18) Вспомнить, когда была ошибка TypeError (в апишке или в репо)
19) Вместо json использовать orjson (или другие альтернативы). Если вообще нужен будет
21) До конца реализовать базовый репо, добавить модели для редактирования.
23) Иногда при исключениях в логах:  PydanticJsonSchemaWarning: Default value annotation=NoneType required=True json_schema_extra={} is not JSON serializable; excluding default from JSON schema [non-serializable-default]
warnings.warn(message, PydanticJsonSchemaWarning)