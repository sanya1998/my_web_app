Добавить переменные окружения в `envs/local.env` (В качестве примера взять `envs/base.env`)

Запуск Docker-контейнеров со сборкой (без API): `make build-related-services`

Можно выполнить тесты, которые предварительно выполнят миграции и заполнят бд: `make run-tests`

Можно вручную выполнить миграции на локальную базу данных: `make forward_migrations_head_local`

Запустить API-сервер вне Docker: `python manage.py runserver`

Swagger: `http://localhost:8010/docs`

Панель администратора: `http://localhost:8010/admin/`

Запустить celery worker вне Docker:

`make up-celery-worker`

Запустить celery flower вне Docker:

`make up-celery-flower`

Веб-интерфейс celery flower http://localhost:5555

Очень простой фронт (2 вида):
- открыть в браузере http://localhost:8010/api/v1/pages/hotels
- см. frontend/README.md (react)

Настройка grafana:
- Перейти по http://localhost:9090/targets и убедиться, что присутствует endpoint http://api:8010/metrics
- Перейти по http://localhost:3000/
- Авторизоваться с логином и паролем из env, обновить страницу
- Перейти в Configuration -> Data sources
- Нажать 'Add data source'
- Нажать 'Prometheus'
- В поле URL написать: 'http://prometheus:9090' (Хост из docker-compose)
- Нажать 'Save & test'
- Из адресной строки скопировать идентификатор (-__JdkANk из http://localhost:3000/datasources/edit/-__JdkANk)
- Открыть файл monitoring/simple-grafana-dashboard.json
- В "panels", в "datasource" заменить все uid на скопированный (-__JdkANk). Это удобно делать через "Найти и заменить"
- Перейти Dashboards -> Import
- Вставить monitoring/simple-grafana-dashboard.json, либо его содержимое
- Нажать 'Load' 
- Нажать 'Import'
- Сделать несколько запросов к API, чтобы появились данные для графиков

Первый Debug в PyCharm (TODO: Можно ли с помощью .idea закинуть в git готовую конфигурацию (что будет с паролями?)):
1. Создать новую конфигурацию для Python
2. Выбрать интерпретатор Python
3. Указать путь до скрипта `manage.py`
4. Добавить аргумент (для runserver: "runserver"; для run_consumer: "run-consumer")
5. Указать рабочую директорию - корень проекта
6. Указать путь до одного из .env-файлов в директории `envs/`
7. Запустить Debug

Некоторые команды из Makefile не запускаются через конфигурацию Makefile, т.к. там не подключается виртуальное окружение.
Запуск таких команд из Makefile в PyCharm (TODO: через python-скрипт):
1. Создать конфигурацию для Shell Script
2. Выбрать Script Text
3. Ввести команду в текстовое поле, например `make alembic_upgrade_head`
4. Выполнить конфигурацию

Инструкция по деплою веб-приложения.
- Создать облачный сервер (например, на https://timeweb.cloud выбрать debian 12, тариф за 150руб, за 150 рублей взять публичный ipv4).
- Войти в консоль, ввести логин (root) и пароль из лк.
- Установить докер и докер-компус (инструкция для debian 12: https://dockerhosting.ru/blog/ustanovka-docker-na-debian-12/)
- - при копировании в консоль двойные кавычки переделались в одинарные, нужно вернуть двойные (в 3 местах).
- - предупреждение об устаревшем способе хранения ключей решается:
- - - `cd /etc/apt`
- - - `sudo cp trusted.gpg trusted.gpg.d`
- склонировать репозиторий (git clone https://github.com/sanya1998/my_web_app.git)
- создать env файл: `touch my_web_app/envs/dev.env` (TODO: копировать по ssh)
- записть переменные окружения в новый файл: nano my_web_app/envs/dev.env
- установить make: `apt install make`
- запустить подготовленную сборку `make build-dev-app`
- перейти по http://109.73.207.254:8010/docs
- накатить миграцию локально (TODO: запускать на сервере):
- - `export $(grep -v '^#' envs/base.env | xargs)`
- - `export $(grep -v '^#' envs/dev.env | xargs)`
- - `alembic upgrade head`
- настроить grafana и prometheus

Проект разрабатывается с помощью курса https://stepik.org/course/153849/promo

TODO:
1) Посмотреть все TODO в коде
2) Придумать причину использовать fastapi lifespan (resource.setup() and resource.close())
3) Проверять подключение к бд при старте приложения (Lifespan) (ping)
4) придумать что-нибудь с submodule (например, модели) и со своей библиотекой
6) ! Перейти на SQLModel
9) id: uuid.UUID
11) pre-commit
13) Разобраться с енвами для бд (число пулов и тд)
16) Ошибки писать в логи, в sentry, kibana (подробно, с трейсом)
17) Сериализация исключений. Что-то про респонс-модел
18) Вспомнить, когда была ошибка TypeError (в апишке или в репо)
19) Вместо json использовать orjson (или другие альтернативы). Если вообще нужен будет. Некоторые почему-то добавляют && poetry install --no-interaction --no-ansi -E orjson
21) До конца реализовать базовый репо.
26) rooms - это, скорее тип комнаты, а не сама комната, потому что в отеле есть определенный тип (категория) комнаты и определенное количество таких комнат
27) pydantic_factory можно использовать для быстрой генерации данных
30) Одна из ошибок не ловилось в ручке catcher-ом. Из-за отсутствия `await` ошибка в `return booking_service.create_booking(booking_input, user_id=user.id)`
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
45) Вычисляемые поля бд сделать только для чтения в админке
46) Конфигурационные файлы ini, может быть, в одну директорию https://stackoverflow.com/questions/12756976/use-different-ini-file-for-alembic-ini или в pyproject.toml
47) Возможно, правильнее использовать статус код HTTP_201_CREATED после создания
48) Перед использованием соединения пингует БД (SELECT 1), если соединение мертво, оно будет закрыто DB_POOL_PRE_PING: bool = True
49) В декоратор роутера вставлять dependencies=, которые не используются внутри ендпоинта
50) mypy попробовать
51) вместо того чтобы писать алгоритм создания конфигурации, добавить в git директорию .idea, если это безопасно
52) ! Аутентификацию в апи через from fastapi.security import APIKeyHeader
53) Мб разобрать депенденси? ресурсы в ресурсы, модели в нужные папки к хэндлерам... как и исключения
54) После того, как вынес все отношения между таблицами в init, в админке стали подчеркиваться поля отношений (Bookings.user)
55) Добавить схему в readme https://stackoverflow.com/questions/14494747/how-to-add-images-to-readme-md-on-github
56) Скрипт, который проверяет, что во всех енвах (В тч проверку для k8s) одни и те же переменные. И в pre-commit
57) Что будет, если вычисляемое POSTGRES_URL записать в енвы сразу целиокм?
60) использовать filters как свою либу.
61) бронирование делать внутри транзакции
63) мб применить from sqlalchemy.inspection import inspect; thing_relations = inspect(Thing).relationships.items()
68) В mocker.patch передается путь (в 2 местах) в виде строки. А путь может поменяться. Подумать над этим
71) Можно ли response_model_by_alias задать сразу для нескольких эндпоинтов? почитать про check populate_by_name=True
72) pyright выдает много ошибок в коде. по возможности пофиксить
73) в сообщениях в hawk фильтровать передаваемые данные (например, с помощью before_send), добавить release, Environments
74) ловить все исключения в ручках (втч при передаче аргументов в депенденси), чтоб трейс не вылазил в ответе ручки. 
75) add_hawk_fastapi уже решает проблему выше, но что если его не будет? пробовать с помощью средств fastapi  
75) при этом проверить, что когда мы ловим все, чтоб ожидаемые исключения тоже работали (например 404)
76) пофиксить в тестах warning, связанный с pythonjsonlogger
83) кеш на комнаты
84) при экспорте данных из бд в csv русские символы превращаются в абракадабру
86) прометеус можно попробовать 3 версии, также глянуть последнюю версию графаны
87) порт и хост в прометеус yml можно ли вытащить в енвы мб??
89) попробовать prometheus.yml копировать, а не передавать в volumes
90) PROMETHEUS_PORT не задается в для прометеуса внутри контейнера
91) создать дашборд для графаны самому.
92) можно ли автоматизировать подключение графаны к прометеусу?
93) можно ли автоматизировать добавление дашборда в графану?
94) порт 3000 у графаны и у фронта. что-то сделать с этим
95) для общего развития можно использовать JSON в столбце бд
96) поработать с вебсокетами
97) познакомиться с Invoke (альтернатива Makefile)
99) можно ли хорошо протестировать отправку сообщения на электронную почту mailhog. 265 стр в книге "Паттерны разработки на Python"
100) Дебагом проверить @computed_field @property в pydantic_settings кешируется? try `from functools import cached_property`
101) почитать про SettingsConfigDict(env_prefix=
102) добавить тесты для фоновых задач (celery and fastapi background)
105) 500 при создании отеля авторизованным пользователем без роли модератора
106) продумать систему хранения, добавления изображения (медиа), связь с отелями через image_id
107) "Send empty value" для числа отправляет null, а для списка одно пустое значение внутри списка. Баг?
108) `integer | (integer | null)` в свагере хотя используется form из библиотеки. Баг?
109) также стоит обратить внимание на `array<[integer, integer], any>`. Баг?
112) где-нибудь использовать Body(embed=True), а не Form. + Несколько примеров с заголовком https://fastapi.tiangolo.com/tutorial/schema-extra-example/#using-the-openapi_examples-parameter
113) в русской версии не все https://fastapi.tiangolo.com/ru/tutorial/schema-extra-example/#body-examples
114) удалить node_modules из github
115) реализовать добавление фото, видео для комнат (отели частично реализованы), не забыть про то, что изображения уже используются