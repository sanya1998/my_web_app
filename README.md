Запретить отслеживать изменения в .env-файлах. 

`git update-index --assume-unchanged .envs/*`

Запуск сервисов локально:

`make up-services`

Выполнить миграции на локальную базу данных:

`make local_migrations`

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

6) local_migrations не выполняется, хотя ее состоавляющие выполняются. понять почему
