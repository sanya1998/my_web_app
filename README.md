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
1) К бд сделать подключению через `@app.on_event("startup")` и сразу создавать пул
2) Все миграции откатить до начала и готовую бд сделать первой ревизией
`alembic revision --autogenerate -m "Initial migration"`
3) создать example.env (?)
4) придумать что-нибудь с submodule (например, модели) и со своей библиотекой
5) Lifespan для fast api
6) Перейти на SQLModel
