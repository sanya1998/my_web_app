Запуск сервисов локально:

`make up-services`

Выполнить миграции на локальную базу данных:

`make forward_migrations_head_local`

Запустить API-сервер:

`python manage.py runserver`

Первый Debug в PyCharm:
1. Создать новую конфигурацию для Python
2. Выбрать интерпретатор Python
3. Указать путь до скрипта `manage.py`
4. Добавить аргумент (для runserver: "runserver"; для run_consumer: "run-consumer")
5. Указать рабочую директорию - корень проекта
6. Указать путь до одного из .env-файлов в директории `envs/`
7. Запустить Debug

Swagger: `http://localhost:8010/docs`

Панель администратора: `http://localhost:8010/admin/`

Некоторые команды из Makefile не запускаются через конфигурацию Makefile, т.к. там не подключается виртуальное окружение.
Запуск таких команд из Makefile в PyCharm (TODO: через python-скрипт):
1. Создать конфигурацию для Shell Script
2. Выбрать Script Text
3. Ввести команду в текстовое поле, например `make alembic_upgrade_head`
4. Выполнить конфигурацию

Запустить celery worker:

`make up-celery-worker`

Запустить celery flower:

`make up-celery-flower`

Веб-интерфейс celery flower http://0.0.0.0:5555

Очень простой фронт (2 вида):
- открыть в браузере http://localhost:8010/api/v1/pages/hotels
- см. frontend/README.md (react)

Проект разрабатывается с помощью курса https://stepik.org/course/153849/promo

TODO:
1) Посмотреть все TODO в коде
2) Найти причину использовать fastapi lifespan (resource.setup() and resource.close())
3) Проверять подключение к бд при старте приложения (Lifespan) (ping)
2) Все миграции откатить до начала и готовую бд сделать первой ревизией
`alembic revision --autogenerate -m "Initial migration"`
3) создать example.env
4) придумать что-нибудь с submodule (например, модели) и со своей библиотекой
6) Перейти на SQLModel
9) id: uuid.UUID
11) pre-commit
13) Разобраться с енвами для бд (число пулов и тд)
15) Написать свой json сериалайзер, чтоб не делать json.loads(json.dumps(
16) Ошибки писать в логи, в sentry, kibana (подробно, с трейсом)
17) Сериализация исключений. Что-то про респонс-модел
18) Вспомнить, когда была ошибка TypeError (в апишке или в репо)
19) Вместо json использовать orjson (или другие альтернативы). Если вообще нужен будет
21) До конца реализовать базовый репо.
26) rooms - это, скорее тип комнаты, а не сама комната, потому что в отеле есть определенный тип (категория) комнаты и определенное количество таких комнат
27) pydantic_factory можно использовать для быстрой генерации данных
30) Одна из ошибок не ловилось в ручке catcher-ом. Из-за отсутствия `await` ошибка в `return booking_service.create_booking(booking_input, user_id=user.id)`
31) Заново создать бд, запустить dump.sql скрипт. Он создаст 3 пользователя. Потом с помощью ручки sign_up добавить пользователя. Будет ругаться на попытку сгенерировать существующий id. 3 раза ручка возвращает ошибку, а на 4ый раз создает
32) дело в sqlalchemy или в postgres?
32) поиграть с ручками, когда таблицы будут пустыми
33) во все методы прописать типы для параметров
35) почитать про aioredis[hiredis], в проекте используется redis.asyncio
36) Приложения, консьюмеры и тд из manage.py запустить в докере (+celery) (например, запустить как utils/linters)
37) Для celery можно почитать https://github.com/celery/celery/issues/8724, чтобы задать корректно разрешения
38) Залесть на сайт docker на python (почитать про alpine, bookworm и тд)
39) Flower не показывает задачи со state "started". Только после выполнения показывает задачи со state "success"
40) Поработать с двумя очередями celery https://habr.com/ru/articles/269347/
42) Почитать доку https://aminalaee.dev/sqladmin/
43) Понять разницу backref и back_populates в sqlalchemy.orm.relationship
44) Сравнить request.session.update({settings.JWT_COOKIE_NAME: access_token}) и response.set_cookie(key=settings.JWT_COOKIE_NAME, value=access_token, httponly=True)
45) Подсчитываемые поля бд сделать только для чтения в админке
46) Конфигурационные файлы ini, может быть, в одну директорию https://stackoverflow.com/questions/12756976/use-different-ini-file-for-alembic-ini или в pyproject.toml
47) Возможно, правильнее использовать статус код HTTP_201_CREATED после создания
48) Перед использованием соединения пингует БД (SELECT 1), если соединение мертво, оно будет закрыто DB_POOL_PRE_PING: bool = True
49) В декоратор роутера вставлять dependencies=, которые не используются внутри ендпоинта
50) mypy попробовать
51) вместо того чтобы писать алгоритм создания конфигурации, добавить в git директорию .idea, если это безопасно
52) Аутентификацию в апи через from fastapi.security import APIKeyHeader
53) Мб разобрать депенденси? ресурсы в ресурсы, модели в нужные папки к хэндлерам... как и исключения
54) После того, как вынес все отношения между таблицами в init, в админке стали подчеркиваться поля отношений (Bookings.user)
55) Добавить схему в readme https://stackoverflow.com/questions/14494747/how-to-add-images-to-readme-md-on-github
56) Скрипт, который проверяет, что во всех енвах (В тч проверку для k8s) одни и те же переменные. И в pre-commit
57) CELERY_BROKER_URL целиком. А остальные разделены на юзер, пароль, хост и тд
60) использовать filters как свою либу.
61) бронирование делать внутри транзакции
63) мб применить from sqlalchemy.inspection import inspect; thing_relations = inspect(Thing).relationships.items()
67) все print() заменить на logger
68) В mocker.patch передается путь (в 2 местах) в виде строки. А путь может поменяться. Подумать над этим
71) Можно ли response_model_by_alias задать сразу для нескольких эндпоинтов? почитать про check populate_by_name=True
72) pyright выдает много ошибок в коде. по возможности пофиксить
73) в сообщениях в hawk фильтровать передаваемые данные (например, с помощью before_send), добавить release, Environments
74) ловить все исключения в ручках (втч при передаче аргументов в депенденси), чтоб трейс не вылазил в ответе ручки. 
75) add_hawk_fastapi уже решает проблему выше, но что если его не будет? пробовать с помощью средств fastapi  
75) при этом проверить, что когда мы ловим все, чтоб ожидаемые исключения тоже работали (например 404)