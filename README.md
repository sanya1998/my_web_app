## Начало работы:
- Добавить переменные окружения в `envs/local.env` (В качестве примера использовать `envs/base.env`)
- Запуск Docker-контейнеров со сборкой (без API): `make build-related-base-services`
- Можно выполнить тесты, которые предварительно выполнят миграции и заполнят бд: `make run-tests`
- Можно вручную выполнить миграции на локальную базу данных: `make forward_migrations_head_local`
- Запустить API-сервер вне Docker: `python manage.py runserver`
- Swagger: `http://localhost:8001/docs`
- Панель администратора: `http://localhost:8001/admin/`
- Запустить celery worker вне Docker: `make up-celery-worker`
- Запустить celery flower вне Docker: `make up-celery-flower`
- Веб-интерфейс celery flower http://localhost:5555

### Очень простой фронт (2 вида):
- открыть в браузере http://localhost:8001/api/v1/pages/hotels
- см. frontend/README.md (react)

### Настройка grafana:
- Перейти по http://localhost:9090/targets и убедиться, что присутствует endpoint http://api:8001/metrics
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

### Первый Debug в PyCharm 
(TODO: Можно ли с помощью .idea закинуть в git готовую конфигурацию (что будет с паролями?)):
1. Создать новую конфигурацию для Python
2. Выбрать интерпретатор Python
3. Указать путь до скрипта `manage.py`
4. Добавить аргумент (для runserver: "runserver"; для run_consumer: "run-consumer")
5. Указать рабочую директорию - корень проекта
6. Указать путь до одного из .env-файлов в директории `envs/`
7. Запустить Debug

### Некоторые команды из Makefile не запускаются через конфигурацию Makefile, т.к. там не подключается виртуальное окружение.
Запуск таких команд из Makefile в PyCharm (TODO: через python-скрипт):
1. Создать конфигурацию для Shell Script
2. Выбрать Script Text
3. Ввести команду в текстовое поле, например `make alembic_upgrade_head`
4. Выполнить конфигурацию

### Инструкция по деплою веб-приложения.
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
- перейти по http://109.73.207.254:8001/docs (TODO: разобраться)
- накатить миграцию локально (TODO: запускать на сервере):
- - `export $(grep -v '^#' envs/base.env | xargs)`
- - `export $(grep -v '^#' envs/dev.env | xargs)`
- - `alembic upgrade head`
- настроить grafana и prometheus

#### Проект разрабатывается с помощью курса https://stepik.org/course/153849/promo

## TODO:

### Refactoring
1) Посмотреть все TODO в коде
2) aioredis to aredis, чтобы не путать с либой
3) is_exists переименовать в exists
4) научиться делать middlewares в виде классов
6) нельзя ли в тестах красиво заполнять {object_id} через экранирование, а не подстановкой
7) "Send empty value" для числа отправляет null, а для списка одно пустое значение внутри списка. Баг? `integer | (integer | null)` в свагере хотя используется form из библиотеки. Баг? также стоит обратить внимание на `array<[integer, integer], any>`. Баг?
8) почитать про SettingsConfigDict(env_prefix=
9) при экспорте данных из бд в csv русские символы превращаются в абракадабру
10) мб применить from sqlalchemy.inspection import inspect; thing_relations = inspect(Thing).relationships.items()
11) В mocker.patch передается путь (в 2 местах) в виде строки. А путь может поменяться. Подумать над этим
12) Можно ли response_model_by_alias задать сразу для нескольких эндпоинтов? почитать про check populate_by_name=True
13) pyright выдает много ошибок в коде. по возможности пофиксить
14) в сообщениях в hawk фильтровать передаваемые данные (например, с помощью before_send), добавить release, Environments
15) hawk в рабочем состоянии не пишет в консоль ошибки, трейс и тд
16) пофиксить в тестах warning, связанный с pythonjsonlogger
17) Мб разобрать папку депенденси и исключения (хотя много общих)? ресурсы в ресурсы, модели в нужные папки к хэндлерам...
18) вместо того чтобы писать алгоритм создания конфигурации, добавить в git директорию .idea, если это безопасно
19) во все методы прописать типы для параметров
20) Сравнить request.session.update({settings.JWT_COOKIE_NAME: access_token}) и response.set_cookie(key=settings.JWT_COOKIE_NAME, value=access_token, httponly=True)
21) Вычисляемые поля бд сделать только для чтения в админке
22) Конфигурационные файлы ini, может быть, в одну директорию https://stackoverflow.com/questions/12756976/use-different-ini-file-for-alembic-ini или в pyproject.toml. (Мб пригодится script_location = alembic)
23) pydantic_factory можно использовать для быстрой генерации данных
24) rooms - это, скорее тип комнаты, а не сама комната, потому что в отеле есть определенный тип (категория) комнаты и определенное количество таких комнат
25) решить проблему при запуске fastapi "GET /favicon.ico HTTP/1.1" 404 Not Found
26) При включенном vpn не дернулась ручка локально, не открывается rmq gui
27) Этот README.md преобразовать так, чтоб была простая инструкция, как равзернуть все в докере, и инструкция для локальных экспериментов (добавить сюда же frontend/README.md)

### Celery. Flower.
1) Для celery можно почитать https://github.com/celery/celery/issues/8724, чтобы задать корректно разрешения
2) Flower не показывает задачи со state "started". Только после выполнения показывает задачи со state "success"
3) Поработать с двумя очередями celery https://habr.com/ru/articles/269347/

### Logs
1) чтобы трейс был удобным, мб и не надо ловить BaseRepoError и BaseServiceError, мб catcher вообще не нужен, если есть Exception
2) Одна из ошибок не ловилось в ручке catcher-ом. Из-за отсутствия `await` ошибка в `return booking_service.create_booking(booking_input, user_id=user.id)`
3) Ошибки писать в логи, в sentry, kibana (подробно, с трейсом)
4) Вспомнить, когда была ошибка TypeError (в апишке или в репо)

### Docker
1) разобраться с портами в docker-compose.yml, что нужно в енвы, что нет. Если изменить порт в енвах, то перестанет работать? 
2) можно использовать hostname в докер-компус, если есть какое-то дублирование
3) Попробовать взять sentry из https://hub.docker.com
4) Залезть на сайт docker на python (почитать про alpine, bookworm и тд)

### Grafana. Prometheus.
1) прометеус можно попробовать 3 версии, также глянуть последнюю версию графаны
2) порт и хост в прометеус yml можно ли вытащить в енвы мб??
3) попробовать prometheus.yml копировать, а не передавать в volumes
4) PROMETHEUS_PORT не задается в для прометеуса внутри контейнера
5) создать дашборд для графаны самому.
6) можно ли автоматизировать подключение графаны к прометеусу?
7) можно ли автоматизировать добавление дашборда в графану?

### DB
1) ! Перейти на SQLModel
2) можно ли как-то индексировать таблицу в бд, чтоб быстро сортировалось по полю? время выполнения запроса. просто добавить индексы
3) можно ли будет импортировать данные из таблицы истории запросов 
4) научиться пользоваться алембиком, когда имеется две бд (news_migrator)
5) алембик работает с асинхронным драйвером почему-то без async_engine_from_config. Смотри пример в проекте news-migrator
6) Потокобезопасный async_scoped_session (news-migrator)
7) почему бд создаю не с помощью create_async_pool_from_url
8) использовать схему таблиц в бд (см news_migrator)
9) вот так по названию можно получать таблицу table_ = metadata.tables.get(table_name_) и await mysql_session.execute(insert(table_).values(rows_))
10) Разобраться с енвами для бд (число пулов и тд)
11) После того, как вынес все отношения между таблицами в init, в админке стали подчеркиваться поля отношений (Bookings.user)
12) Проверять подключение к бд при старте приложения (Lifespan) (ping)
13) Перед использованием соединения пингует БД (SELECT 1), если соединение мертво, оно будет закрыто DB_POOL_PRE_PING: bool = True
14) Почитать доку https://aminalaee.dev/sqladmin/
15) Понять разницу backref и back_populates в sqlalchemy.orm.relationship

### Rabbitmq
1) запускать rmq консьюмер как starlette, если будет необходимость
2) реализовать sse таким образом, чтобы не было нагрузки на процессор sleep-ом, чтоб генератор работал только по событию. Консьюмер rmq можно, но, вероятно, будет ограничение пула.
3) написать тесты на консьюмер
4) написать воркер, который при большом количестве сообщений (queue.declaration_result.message_count) в очереди кролика будет отправлять аллерт в телеграм, а потом сам его убирать, если очередь разгрузится
5) api и консьюмер перезапускаются (restart: on-failure:5), пока не заработает rabbitmq (или 5 попыток), в логи пишут ошибки подключения. Можно ли дождаться полного запуска rabbitmq и не писать ошибки в логи?

### Pre-commit
1) линтеры, тесты
2) добавить то, что алембиком создана последняя миграция и больше не было изменений, а также что docker-compose имеют все сервисы одинаковые (warning)
3) Скрипт, который проверяет, что во всех енвах (В тч проверку для k8s) одни и те же переменные.

### Frontend
1) Написать тесты на фронт
2) На фронте, если открыть страницу и следить в нетворкс, то ручка два раза дергается, + есть 2 редиректа

### Feature
1) реализовать добавление фото, видео для комнат (отели частично реализованы), не забыть про то, что изображения уже используются
2) кеш на комнаты
3) бронирование делать внутри транзакции
4) Скриптом замерить скорости ответов ручек, проверить с ORJSONResponse и без
5) Рассмотреть возможность передавать ошибки в responses. Выбрать оптимальный вариант. Вероятно, в свагере появятся
6) где-нибудь использовать Body(embed=True), а не Form. + Несколько примеров с заголовком https://fastapi.tiangolo.com/tutorial/schema-extra-example/#using-the-openapi_examples-parameter
7) продумать систему хранения и добавления изображения (медиа), связь с отелями через image_id
8) добавить тесты для фоновых задач (celery and fastapi background)
9) До конца реализовать базовый репо.
10) id: uuid.UUID
11) В приветственных логах api написать ссылку на сваггер, чтобы не делать лишних переходов

### NEW
1) в русской версии не все https://fastapi.tiangolo.com/ru/tutorial/schema-extra-example/#body-examples
2) Что будет, если вычисляемое POSTGRES_URL записать в енвы сразу целиокм?
3) поработать с вебсокетами
4) познакомиться с Invoke (альтернатива Makefile)
5) для общего развития можно использовать JSON в столбце бд
6) Дебагом проверить @computed_field @property в pydantic_settings кешируется? try `from functools import cached_property`
7) можно ли хорошо протестировать отправку сообщения на электронную почту mailhog. 265 стр в книге "Паттерны разработки на Python"
8) mypy попробовать
9) почитать про aioredis[hiredis], в проекте используется redis.asyncio
10) использовать http2 protocol вместо http/1.1  (https://readmedium.com/deploy-fastapi-with-hypercorn-http-2-asgi-8cfc304e9e7a) (https://pypi.org/project/Hypercorn/)
11) можно ли бесплатно сделать https, есть мидлвэйр для проверки HTTPSRedirectMiddleware.
12) рассмотреть BrotliMiddleware
13) airium · PyPI создать html на python https://pypi.org/project/airium/
14) использовать filters как свою либу.
15) придумать что-нибудь с submodule (например, модели) и со своей библиотекой
16) Почитать про строку scope в форме с username и password  (users:read или users:write)
17) Добавить схему в readme https://stackoverflow.com/questions/14494747/how-to-add-images-to-readme-md-on-github
