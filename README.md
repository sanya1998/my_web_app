Запуск сервисов локально:

`make up-services`

Выполнить миграции на локальную базу данных:

`make forward_migrations_head_local`

Первый Debug в pycharm:
1. Создать новую конфигурацию для Python
2. Выбрать интерпретатор Python
3. Указать путь до скрипта `manage.py`
4. Добавить аргумент (для runserver: "runserver"; для run_consumer: "run-consumer")
5. Указать рабочую директорию - корень проекта
6. Указать путь до одного из .env-файлов в директории `.envs/`
7. Запустить Debug

Запретить отслеживать изменения в .env-файлах. 

`git update-index --assume-unchanged .envs/*`

Проект разрабатывается с помощью курса https://stepik.org/course/153849/promo

TODO:
1) К бд сделать подключению через `@app.on_event("startup")` и сразу создавать пул
2) Линтеры
3) Поменять шаблон файлов ревизий (чтобы в начале названия была смысловая часть)
4) Все миграции откатить до начала и готовую бд сделать первой ревизией
`alembic revision --autogenerate -m "Initial migration"`
5) В .env alembic-а нужно, чтоб логирование не настраивалось при тестах

`# This line sets up loggers basically.
if not strtobool(os.environ.get("TEST", "false")):`

6) local_migrations не выполняется, хотя ее составляющие выполняются. понять почему
7) создать example.env (?)
8) придумать что-нибудь с submodule (например, модели) и со своей библиотекой
9) команды из Makefile не выполняются через конфигурацию pycharm, но выполняются в обычном терминале
10) Lifespan для fast api
