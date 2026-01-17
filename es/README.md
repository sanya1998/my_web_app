# Elasticsearch DSL - Шпаргалка

## Содержание

<pre>
📋 <a href="#запросы-query">ЗАПРОСЫ (QUERY)</a>
│
├── <a href="#полнотекстовый-поиск">Полнотекстовый поиск</a>
│   ├── <a href="#match">Match</a> - 📝 Поиск с анализом текста
│   ├── <a href="#matchphrase">MatchPhrase</a> - 📝 Поиск точной фразы
│   ├── <a href="#matchphraseprefix">MatchPhrasePrefix</a> - 📝 Поиск по префиксу фразы
│   ├── <a href="#multimatch">MultiMatch</a> - 🔍 Поиск по нескольким полям
│   ├── <a href="#querystring">QueryString</a> - 🔤 Расширенный строковый запрос
│   └── <a href="#simplequerystring">SimpleQueryString</a> - 🔤 Упрощенный строковый запрос
│
├── <a href="#терминовый-поиск">Терминовый поиск</a>
│   ├── <a href="#term">Term</a> - 🔤 Точное совпадение термина
│   ├── <a href="#terms-запрос">Terms</a> - 🔤 Несколько терминов
│   ├── <a href="#range">Range</a> - 📊 Диапазон значений
│   ├── <a href="#prefix">Prefix</a> - 🔍 Поиск по префиксу
│   ├── <a href="#wildcard">Wildcard</a> - 🃏 Поиск с подстановкой (*, ?)
│   ├── <a href="#regexp">Regexp</a> - 🧮 Регулярные выражения
│   └── <a href="#exists">Exists</a> - ✅ Проверка существования поля
│
├── <a href="#составные-запросы">Составные запросы</a>
│   ├── <a href="#bool">Bool</a> - 🧩 Логические операторы
│   ├── <a href="#boosting">Boosting</a> - 📈 Усиление/ослабление запросов
│   ├── <a href="#constantscore">ConstantScore</a> - ⚖️ Фиксированная релевантность
│   ├── <a href="#dismax">DisMax</a> - 🏆 Объединение запросов с макс. score
│   └── <a href="#functionscore">FunctionScore</a> - 🧮 Кастомный расчет релевантности
│
└── <a href="#специализированные-запросы">Специализированные запросы</a>
    ├── <a href="#nested">Nested</a> - 🏗️ Вложенные объекты
    ├── <a href="#geoquery">GeoQuery</a> - 🌍 Географический поиск
    ├── <a href="#scriptquery">ScriptQuery</a> - 📜 Скриптовый запрос
    ├── <a href="#morelikethis">MoreLikeThis</a> - 🔄 Поиск похожих документов
    └── <a href="#percolate">Percolate</a> - 💧 Обратный поиск

📊 <a href="#агрегации-aggregation">АГРЕГАЦИИ (AGGREGATION)</a>
│
├── <a href="#бакетные-агрегации-группировка">Бакетные агрегации (группировка)</a>
│   ├── <a href="#terms">Terms</a> - 📊 Группировка по значениям
│   ├── <a href="#range-агрегация">Range</a> - 📈 Группировка по диапазонам
│   ├── <a href="#datehistogram">DateHistogram</a> - 📅 Группировка по времени
│   ├── <a href="#daterange">DateRange</a> - 📆 Диапазоны дат
│   ├── <a href="#histogram">Histogram</a> - 📐 Числовые интервалы
│   ├── <a href="#geohashgrid">GeoHashGrid</a> - 🌍 Географическая сетка
│   ├── <a href="#nested-агрегация">Nested</a> - 🏗️ Вложенные агрегации
│   ├── <a href="#reversenested">ReverseNested</a> - ↩️ Обратные вложенные
│   └── <a href="#filter-агрегация">Filter</a> - 🔍 Агрегации с фильтром
│
├── <a href="#метрические-агрегации-вычисления">Метрические агрегации (вычисления)</a>
│   ├── <a href="#stats">Stats</a> - 📈 Базовая статистика
│   ├── <a href="#extendedstats">ExtendedStats</a> - 📊 Расширенная статистика
│   ├── <a href="#avg">Avg</a> - ➗ Среднее значение
│   ├── <a href="#sum">Sum</a> - ➕ Сумма
│   ├── <a href="#min">Min</a> - 📉 Минимум
│   ├── <a href="#max">Max</a> - 📈 Максимум
│   ├── <a href="#cardinality">Cardinality</a> - 🔢 Уникальные значения
│   ├── <a href="#valuecount">ValueCount</a> - 🔢 Подсчет всех значений
│   ├── <a href="#percentiles">Percentiles</a> - 📊 Процентили
│   └── <a href="#percentileranks">PercentileRanks</a> - 🏆 Ранги процентилей
│
└── <a href="#конвейерные-агрегации">Конвейерные агрегации</a>
    ├── <a href="#avgbucket">AvgBucket</a> - ➗ Среднее по группам
    ├── <a href="#sumbucket">SumBucket</a> - ➕ Сумма по группам
    ├── <a href="#minbucket">MinBucket</a> - 📉 Минимум по группам
    ├── <a href="#maxbucket">MaxBucket</a> - 📈 Максимум по группам
    ├── <a href="#statsbucket">StatsBucket</a> - 📊 Статистика по группам
    ├── <a href="#cumulativesum">CumulativeSum</a> - 🧮 Накопительная сумма
    ├── <a href="#derivative">Derivative</a> - 📈 Изменение между группам
    └── <a href="#movingavg">MovingAvg</a> - 📉 Скользящее среднее

🔧 ДОПОЛНИТЕЛЬНЫЕ РАЗДЕЛЫ
├── <a href="#построение-запросов">Построение запросов</a>
├── <a href="#полезные-советы">Полезные советы</a>
└── <a href="#частые-ошибки">Частые ошибки</a>
</pre>
---

## <a id="запросы-query"></a>Запросы (Query)

### <a id="полнотекстовый-поиск"></a>Полнотекстовый поиск

#### <a id="match"></a>📝 Match - полнотекстовый поиск

*Параметры:*
- `query` (обязательный) - текст для поиска
- `fuzziness` - допуск опечаток: `"AUTO"` (автоопределение), `0` (точное), `1` (1 ошибка), `2` (2 ошибки)
- `operator` - логика между словами: `"and"` (все слова), `"or"` (любое слово)
- `analyzer` - анализатор текста (стандартный, русский и т.д.)
- `boost` - коэффициент важности (1.0 = нейтрально, 2.0 = в 2 раза важнее)
- `lenient` - игнорировать ошибки формата (True/False)
- `minimum_should_match` - минимальный процент совпадения слов ("75%", 3)
- `zero_terms_query` - поведение при отсутствии совпадений: `"none"` (ничего), `"all"` (все)

*Примеры:*

    ```python
    # Базовое использование
    Match(title={"query": "smartphone", "fuzziness": "AUTO"})
    # или короткая форма
    Match(title="smartphone")

    # Поиск с автоисправлением опечаток
    Match(description={"query": "wirelles charjing", "fuzziness": "AUTO"})

    # Строгий поиск (все слова должны быть)
    Match(title={"query": "wireless headphones", "operator": "and"})

    # Поиск с усилением релевантности
    Match(category={"query": "electronics", "boost": 2.0})
    ```

#### <a id="matchphrase"></a>📝 MatchPhrase - поиск точной фразы

*Параметры:*
- `query` (обязательный) - точная фраза для поиска
- `slop` - максимальное расстояние между словами фразы (0 = точная фраза, 2 = можно вставить 2 слова между)
- `analyzer` - анализатор текста
- `boost` - коэффициент важности

*Отличие от Match:*
- `Match` ищет отдельные слова (wireless ИЛИ charging)
- `MatchPhrase` ищет точную фразу "wireless charging" (слова в правильном порядке)

*Примеры:*

    ```python
    # Базовое использование
    MatchPhrase(description="wireless charging")
    # или с параметрами
    MatchPhrase(description={"query": "wireless charging", "slop": 2})

    # Точная фраза
    MatchPhrase(title="wireless charging")  # найдет "wireless charging", но не "charging wireless"

    # Фраза с допуском
    MatchPhrase(description={"query": "quick brown fox", "slop": 1})
    # найдет "quick brown fox", "quick and brown fox", "quick brown lazy fox"
    ```

#### <a id="matchphraseprefix"></a>📝 MatchPhrasePrefix - поиск по префиксу фразы

*Параметры:*
- `query` (обязательный) - начало фразы
- `max_expansions` - максимальное количество вариантов для поиска (по умолчанию 50)
- `slop` - допуск расстояния между словами
- `analyzer` - анализатор текста

*Применение:* Поиск по началу фразы (autocomplete для фраз)

*Примеры:*

    ```python
    # Базовое использование
    MatchPhrasePrefix(title={"query": "wireless char", "max_expansions": 10})

    # Автодополнение фразы
    MatchPhrasePrefix(description={"query": "quick brown", "max_expansions": 5})
    # найдет: "quick brown fox", "quick brown dog", "quick brown rabbit" и т.д.

    # Поиск с ограничением вариантов
    MatchPhrasePrefix(title={"query": "wireless", "max_expansions": 3})
    ```

#### <a id="multimatch"></a>🔍 MultiMatch - поиск по нескольким полям

*Типы поиска:*
- `best_fields` - (по умолчанию) ищет в любом поле, выбирает лучшее
- `most_fields` - ищет во всех полях, суммирует совпадения
- `cross_fields` - ищет фразу across полей (для адресов, имен)
- `phrase` - точная фраза в любом поле
- `phrase_prefix` - префикс фразы в любом поле

*Параметры:*
- `fields` - список полей (вес через `^`: `"title^3"` = в 3 раза важнее)
- `tie_breaker` - коэффициент связи при равенстве score (0.0-1.0)
- `minimum_should_match` - минимальное совпадение условий

*Примеры:*

    ```python
    # Базовое использование
    MultiMatch(
        query="wireless headphones",
        fields=["title^3", "description^2", "features"],
        type="best_fields"
    )

    # Поиск по всем полям
    MultiMatch(
        query="John Smith",
        fields=["first_name", "last_name", "full_name^2"],
        type="cross_fields"
    )

    # Фразовый поиск по нескольким полям
    MultiMatch(
        query="quick brown fox",
        fields=["title", "content"],
        type="phrase"
    )
    ```

#### <a id="querystring"></a>🔤 QueryString - расширенный строковый запрос

*Специальные операторы:*
- `AND`, `OR`, `NOT` - логические операторы
- `"фраза"` - точная фраза
- `*` - любое количество символов
- `?` - один любой символ
- `~N` - нечеткое совпадение (например: `roam~1` найдет foam, roams)
- `field:value` - поиск в конкретном поле

*Параметры:*
- `query` (обязательный) - строка запроса с операторами
- `default_field` - поле по умолчанию (если не указано в запросе)
- `analyze_wildcard` - анализировать wildcard-запросы
- `allow_leading_wildcard` - разрешить wildcard в начале (*value)
- `fuzziness` - допуск опечаток
- `minimum_should_match` - минимальное совпадение

*Примеры:*

    ```python
    # Базовое использование
    QueryString(
        query='(wireless AND charging) OR "fast charge"',
        default_field="description",
        analyze_wildcard=True
    )

    # Сложный запрос с операторами
    QueryString(
        query='title:(wireless OR bluetooth) AND price:[100 TO 500]',
        default_field="description"
    )

    # Поиск с wildcard и фразами
    QueryString(query='name:"John Smith" AND addres*:street')
    ```

#### <a id="simplequerystring"></a>🔤 SimpleQueryString - упрощенный строковый запрос

*Операторы:*
- `+` - должен быть (AND)
- `|` - или (OR)
- `-` - не должен быть (NOT)
- `*` - wildcard в конце слова
- `"` - фраза

*Параметры:*
- `query` (обязательный) - строка запроса
- `fields` - поля для поиска
- `default_operator` - оператор по умолчанию (`"and"`, `"or"`)
- `analyze_wildcard` - анализировать wildcard

*Особенности:* Более безопасный чем QueryString, игнорирует синтаксические ошибки

*Примеры:*

    ```python
    # Базовое использование
    SimpleQueryString(
        query='wireless +charging -battery',
        fields=["title", "description"],
        default_operator="and"
    )

    # Простой запрос с операторами
    SimpleQueryString(query='wireless +headphones -expensive', fields=["title"])

    # Поиск с альтернативами
    SimpleQueryString(query='bluetooth | wireless | cable', default_operator="or")
    ```

### <a id="терминовый-поиск"></a>Терминовый поиск

#### <a id="term"></a>🔤 Term - точное совпадение

*Параметры:*
- `boost` - коэффициент важности запроса

*Важно:* Для текстовых полей используй `.keyword` для точного совпадения:

*Примеры:*

    ```python
    # Базовое использование
    Term(category="electronics")
    Term(status=True)

    # Для текстовых полей используй .keyword
    # Поле "category" типа text с sub-field keyword
    Term(category__keyword="Smartphone")  # точное совпадение "Smartphone"
    # Вместо (может не найти из-за анализатора):
    Term(category="Smartphone")           # ищет проанализированные токены

    # С усилением релевантности
    Term(category__keyword="premium", boost=2.0)
    ```

#### <a id="terms-запрос"></a>🔤 Terms - несколько терминов

*Параметры:*
- `boost` - коэффициент важности

*Логика:* Находит документы, где поле содержит ЛЮБОЕ из указанных значений

*Примеры:*

    ```python
    # Базовое использование
    Terms(category=["electronics", "phones", "accessories"])
    Terms(status=[True, False])

    # Поиск по нескольким категориям
    Terms(category__keyword=["Smartphone", "Tablet", "Laptop"])

    # Поиск по нескольким статусам
    Terms(status=["active", "pending"])

    # С усилением релевантности
    Terms(tags=["featured", "popular"], boost=1.5)
    ```

#### <a id="range"></a>📊 Range - диапазон значений

*Операторы сравнения:*
- `gt` (greater than) - больше чем
- `gte` (greater than or equal) - больше или равно
- `lt` (less than) - меньше чем
- `lte` (less than or equal) - меньше или равно

*Примеры:*

    ```python
    # Базовое использование
    Range(price={"gte": 100, "lte": 1000})
    Range(date={"gte": "2024-01-01", "lt": "2024-02-01"})

    # Числовые диапазоны
    Range(age={"gt": 18})
    Range(score={"gte": 0, "lte": 100})

    # Диапазоны дат
    Range(created_at={"gte": "2024-01-01", "lt": "2024-01-31"})
    Range(timestamp={"gte": "now-7d/d"})  # последние 7 дней

    # Частичные диапазоны
    Range(price={"gt": 0})  # цена больше 0
    Range(rating={"lte": 5})  # рейтинг до 5
    ```

#### <a id="prefix"></a>🔍 Prefix - поиск по префиксу

*Параметры:*
- `boost` - коэффициент важности

*Применение:* Поиск по началу строки (autocomplete)

*Примеры:*

    ```python
    # Базовое использование
    Prefix(name__keyword="Joh")  # найдет John, Johanna, Johnson

    # Автодополнение названий
    Prefix(product_name__keyword="Smartph")  # Smartphone, Smartphones

    # Поиск по префиксу кода
    Prefix(code="ABC-1")  # ABC-100, ABC-123, ABC-1X

    # С усилением релевантности
    Prefix(title__keyword="Pro", boost=1.2)
    ```

#### <a id="wildcard"></a>🃏 Wildcard - поиск с подстановкой

*Подстановочные символы:*
- `*` - любое количество символов (включая 0)
- `?` - один любой символ

*Параметры:*
- `boost` - коэффициент важности
- `case_insensitive` - регистронезависимый поиск (с Elasticsearch 7.10+)

*Примеры:*

    ```python
    # Базовое использование
    Wildcard(title__keyword="smart*ne")  # smartphone, smartpone, smartphone
    Wildcard(email="*@gmail.com")

    # Поиск с разными вариантами написания
    Wildcard(name__keyword="Sm?th")  # Smith, Smyth

    # Поиск по шаблону
    Wildcard(filename="report_2024_*.pdf")
    Wildcard(log_level="ERROR_*")

    # С параметрами
    Wildcard(title__keyword="test*", boost=1.5, case_insensitive=True)
    ```

#### <a id="regexp"></a>🧮 Regexp - регулярные выражения

*Параметры:*
- `flags` - флаги регулярных выражений (`ALL`, `ANYSTRING`, `COMPLEMENT`, `INTERVAL` и др.)
- `max_determinized_states` - ограничение сложности (по умолчанию 10000)
- `boost` - коэффициент важности

*Примеры:*

    ```python
    # Базовое использование
    Regexp(title__keyword="smart(phone|watch|hub)")

    # Регулярное выражение для поиска email
    Regexp(email="[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

    # Поиск по шаблону даты
    Regexp(date_string="2024-\d{2}-\d{2}")

    # Поиск с флагами
    Regexp(
        field="message",
        value="error.*failed",
        flags="ALL",
        max_determinized_states=5000
    )
    ```

#### <a id="exists"></a>✅ Exists - проверка существования поля

*Параметры:*
- `field` (обязательный) - имя поля для проверки

*Примеры:*

    ```python
    # Базовое использование
    Exists(field="description")

    # Найти документы с заполненным описанием
    Exists(field="description")

    # Найти документы с ценой
    Exists(field="price")

    # В комбинации с Bool
    Bool(must_not=[Exists(field="deleted_at")])  # не удаленные

    # Проверка нескольких условий
    Bool(
        must=[
            Exists(field="title"),
            Exists(field="content")
        ],
        must_not=[Exists(field="draft")]
    )
    ```

### <a id="составные-запросы"></a>Составные запросы

#### <a id="bool"></a>🧩 Bool - логические операторы

*Секции Bool (все списки объединяются оператором И):*
- `must` - ДОЛЖНЫ выполняться ВСЕ условия (влияет на релевантность)
- `filter` - ДОЛЖНЫ выполняться ВСЕ условия (не влияет на релевантность, быстрее)
- `should` - ХОТЯ БЫ ОДНО условие должно выполняться*
- `must_not` - НИ ОДНО условие не должно выполняться

*Правила:*
1. `must` + `filter` + `must_not` = И между всеми условиями
2. `should` работает как ИЛИ внутри своего списка
3. Если есть `must` или `filter`, то `should` становится опциональным (усиливает релевантность)
4. Без `must`/`filter` - хотя бы один `should` должен совпасть (или `minimum_should_match`)

*Score (релевантность):* Число, показывающее насколько документ соответствует запросу. Чем выше - тем релевантнее.

*Примеры:*

    ```python
    # Базовое использование
    Bool(
        must=[Match(title="phone"), Range(price={"lte": 1000})],
        filter=[Term(is_available=True)],
        should=[Term(brand="apple"), Term(brand="samsung")],
        must_not=[Term(color="red")],
        minimum_should_match=1
    )

    # Поиск товаров с фильтрацией
    Bool(
        must=[Match(description="wireless")],
        filter=[
            Range(price={"gte": 50, "lte": 500}),
            Term(in_stock=True),
            Terms(category=["electronics", "audio"])
        ],
        must_not=[Term(is_discontinued=True)]
    )

    # Булев поиск только с should
    Bool(
        should=[
            Match(title="phone"),
            Match(description="smartphone"),
            Match(brand="apple")
        ],
        minimum_should_match=2
    )
    ```

#### <a id="boosting"></a>📈 Boosting - усиление/ослабление запросов

*Параметры:*
- `positive` - основной запрос (обязательный)
- `negative` - запрос для ослабления (обязательный)
- `negative_boost` - коэффициент ослабления (0.0-1.0)

*Логика:* Уменьшает релевантность документов, соответствующих negative запросу

*Примеры:*

    ```python
    # Базовое использование
    Boosting(
        positive=Match(title="phone"),
        negative=Term(brand="cheap_brand"),
        negative_boost=0.2
    )

    # Ослабить документы определенного бренда
    Boosting(
        positive=Match(description="wireless"),
        negative=Term(brand="unknown_brand"),
        negative_boost=0.5  # в 2 раза менее релевантны
    )

    # Ослабить старые товары
    Boosting(
        positive=Match(category="electronics"),
        negative=Range(created_at={"lt": "2023-01-01"}),
        negative_boost=0.7
    )
    ```

#### <a id="constantscore"></a>⚖️ ConstantScore - фиксированная релевантность

*Параметры:*
- `filter` - запрос-фильтр (обязательный)
- `boost` - фиксированный score для всех найденных документов

*Применение:* Когда нужна фильтрация без расчета релевантности, но с фиксированным score

*Примеры:*

    ```python
    # Базовое использование
    ConstantScore(
        filter=Term(category="electronics"),
        boost=1.2
    )

    # Фильтр с фиксированной релевантностью
    ConstantScore(
        filter=Range(price={"gte": 100, "lte": 1000}),
        boost=1.0
    )

    # Комбинированный фильтр
    ConstantScore(
        filter=Bool(
            must=[
                Term(is_active=True),
                Range(rating={"gte": 4.0})
            ]
        ),
        boost=1.5
    )
    ```

#### <a id="dismax"></a>🏆 DisMax - объединение с максимальным score

*Параметры:*
- `queries` - список запросов (обязательный)
- `tie_breaker` - коэффициент для остальных запросов (0.0-1.0)

*Логика:* Выбирает максимальный score из всех запросов, остальные умножает на tie_breaker

*Примеры:*

    ```python
    # Базовое использование
    DisMax(
        queries=[
            Match(title="phone"),
            Match(description="phone")
        ],
        tie_breaker=0.3
    )

    # Поиск в нескольких полях с приоритетом лучшего совпадения
    DisMax(
        queries=[
            Match(title={"query": "apple", "boost": 2}),
            Match(description="apple"),
            Match(brand="apple")
        ],
        tie_breaker=0.5
    )

    # Комбинация разных типов запросов
    DisMax(
        queries=[
            MatchPhrase(title="wireless charging"),
            Match(description="charging"),
            Term(category="electronics")
        ],
        tie_breaker=0.4
    )
    ```

#### <a id="functionscore"></a>🧮 FunctionScore - кастомный расчет релевантности

*Функции:*
- `weight` - умножение score на коэффициент
- `field_value_factor` - использование значения поля
- `random_score` - случайный score
- `script_score` - кастомный скрипт

*Параметры:*
- `score_mode` - как комбинировать функции: `"multiply"`, `"sum"`, `"avg"`, `"max"`, `"min"`
- `boost_mode` - как комбинировать с оригинальным score: `"multiply"`, `"replace"`, `"sum"`, `"avg"`

*Примеры:*

    ```python
    # Базовое использование
    FunctionScore(
        query=Match(title="phone"),
        functions=[
            {
                "filter": Term(brand="apple"),
                "weight": 2
            },
            {
                "field_value_factor": {
                    "field": "rating",
                    "factor": 1.2,
                    "modifier": "sqrt"
                }
            }
        ],
        score_mode="multiply"
    )

    # Усиление по рейтингу и весу
    FunctionScore(
        query=Match(all="restaurant"),
        functions=[
            {
                "field_value_factor": {
                    "field": "rating",
                    "factor": 1.5,
                    "modifier": "log1p"
                }
            },
            {
                "filter": Term(cuisine="italian"),
                "weight": 1.2
            }
        ],
        score_mode="sum"
    )

    # Случайное перемешивание с весом
    FunctionScore(
        query=Match(category="products"),
        functions=[
            {
                "random_score": {},
                "weight": 0.5
            },
            {
                "field_value_factor": {
                    "field": "popularity",
                    "factor": 0.1
                }
            }
        ],
        score_mode="sum",
        boost_mode="multiply"
    )
    ```

### <a id="специализированные-запросы"></a>Специализированные запросы

#### <a id="nested"></a>🏗️ Nested - вложенные объекты

*Логика работы:*
Nested запрос проверяет ВЛОЖЕННЫЕ объекты внутри документа. Документ подходит, если СУЩЕСТВУЕТ ХОТЯ БЫ ОДИН вложенный объект, удовлетворяющий условию.

*Параметры:*
- `path` - путь к nested полю (обязательный)
- `query` - запрос для nested документов (обязательный)
- `score_mode` - как считать релевантность:
  - `"none"` - не считать (только фильтрация)
  - `"avg"` - среднее по nested документам
  - `"sum"` - сумма
  - `"max"` - максимальный score
  - `"min"` - минимальный score

*Примеры:*

    ```python
    # Базовое использование
    Nested(
        path="variants",
        query=Bool(
            must=[
                Term(variants__color="black"),
                Range(variants__stock={"gt": 0})
            ]
        ),
        score_mode="none"
    )

    # Поиск по вложенным тегам
    Nested(
        path="tags",
        query=Bool(
            must=[
                Term(tags__name="electronics"),
                Term(tags__priority="high")
            ]
        )
    )

    # Сложный nested запрос
    Nested(
        path="reviews",
        query=Bool(
            must=[
                Range(reviews__rating={"gte": 4}),
                Match(reviews__text="excellent"),
                Term(reviews__verified=True)
            ]
        ),
        score_mode="avg"
    )
    ```

#### <a id="geoquery"></a>🌍 GeoQuery - географический поиск

*Типы geo-запросов:*
- `GeoDistance` - в радиусе от точки
- `GeoBoundingBox` - в прямоугольной области
- `GeoPolygon` - в полигоне
- `GeoShape` - сложные географические формы

*Примеры:*

    ```python
    # GeoDistance - поиск в радиусе
    GeoDistance(
        location={
            "lat": 55.7558,
            "lon": 37.6173
        },
        distance="10km"
    )

    # GeoBoundingBox - поиск в прямоугольнике
    GeoBoundingBox(
        location={
            "top_left": {"lat": 55.8, "lon": 37.5},
            "bottom_right": {"lat": 55.7, "lon": 37.7}
        }
    )

    # Поиск в радиусе 5 км от центра
    GeoDistance(
        location={"lat": 55.7558, "lon": 37.6173},
        distance="5km",
        distance_type="arc"  # или "plane"
    )

    # Поиск в bounding box
    GeoBoundingBox(
        location={
            "top_left": {"lat": 55.8, "lon": 37.5},
            "bottom_right": {"lat": 55.7, "lon": 37.7}
        },
        type="indexed"  # или "memory"
    )
    ```

#### <a id="scriptquery"></a>📜 ScriptQuery - скриптовый запрос

*Параметры:*
- `script` (обязательный) - скрипт на Painless (язык Elasticsearch)
- `boost` - коэффициент важности

*Примеры:*

    ```python
    # Базовое использование
    Script(
        script={
            "source": "doc['price'].value > params.min_price",
            "params": {"min_price": 100}
        }
    )

    # Сложное условие на скрипте
    Script(
        script={
            "source": """
                doc['price'].value > 100 && 
                doc['rating'].value >= 4.0 &&
                doc['stock'].value > 0
            """
        }
    )

    # Использование параметров
    Script(
        script={
            "source": "doc['price'].value * params.discount > params.min_final_price",
            "params": {"discount": 0.8, "min_final_price": 50}
        }
    )

    # Работа с датами
    Script(
        script={
            "source": """
                LocalDateTime now = LocalDateTime.now(ZoneOffset.UTC);
                LocalDateTime created = doc['created_at'].value;
                ChronoUnit.DAYS.between(created, now) < 30
            """
        }
    )
    ```

#### <a id="morelikethis"></a>🔄 MoreLikeThis - поиск похожих документов

*Параметры:*
- `like` - документы или тексты для сравнения
- `fields` - поля для анализа
- `min_term_freq` - минимальная частота термина в документе
- `max_query_terms` - максимальное количество терминов в запросе
- `min_doc_freq` - минимальная частота документа
- `max_doc_freq` - максимальная частота документа
- `min_word_length` - минимальная длина слова
- `max_word_length` - максимальная длина слова

*Примеры:*

    ```python
    # Базовое использование
    MoreLikeThis(
        like=[
            {"_index": "products", "_id": "123"},
            {"text": "wireless bluetooth headphones with noise cancellation"}
        ],
        fields=["title", "description", "features"],
        min_term_freq=1,
        max_query_terms=25
    )

    # Поиск похожих на существующий документ
    MoreLikeThis(
        like=[{"_index": "articles", "_id": "abc123"}],
        fields=["title", "content"],
        min_term_freq=2,
        max_query_terms=20
    )

    # Поиск по тексту
    MoreLikeThis(
        like=[{"text": "modern smartphone with high resolution camera"}],
        fields=["title", "description"],
        min_doc_freq=1
    )

    # Поиск с настройками
    MoreLikeThis(
        like=[{"_id": "doc1"}, {"_id": "doc2"}],
        fields=["content"],
        min_term_freq=2,
        max_query_terms=30,
        min_doc_freq=5,
        min_word_length=3,
        max_word_length=15
    )
    ```

#### <a id="percolate"></a>💧 Percolate - обратный поиск

*Применение:* Находит запросы, которым соответствует документ (обратный поиск)

*Параметры:*
- `field` - поле с percolator запросами (обязательное)
- `document` - документ для проверки (обязательный)

*Примеры:*

    ```python
    # Базовое использование
    Percolate(
        field="query",
        document={
            "title": "Wireless Headphones",
            "category": "electronics",
            "price": 99.99
        }
    )

    # Проверка, каким запросам соответствует документ
    Percolate(
        field="alerts",
        document={
            "price": 150,
            "category": "electronics",
            "in_stock": True
        }
    )

    # Использование в реальном времени
    Percolate(
        field="subscription_queries",
        document=new_product
    )

    # Сложный документ
    Percolate(
        field="notification_rules",
        document={
            "event_type": "purchase",
            "amount": 1000,
            "currency": "USD",
            "user_category": "premium",
            "location": {"city": "New York", "country": "US"}
        }
    )
    ```
---
## <a id="агрегации-aggregation"></a>Агрегации (Aggregation)

### <a id="бакетные-агрегации-группировка"></a>Бакетные агрегации (группировка)

#### <a id="terms"></a>📊 Terms - группировка по уникальным значениям

*Параметры:*
- `field` - поле для группировки (обязательное)
- `size` - количество возвращаемых групп (по умолчанию 10)
- `order` - сортировка групп:
  - `{"_count": "desc"}` - по количеству документов (убывание)
  - `{"_key": "asc"}` - по значению (возрастание)
  - `{"stats.avg": "desc"}` - по метрике из под-агрегации
- `min_doc_count` - минимальное количество документов в группе
- `include`/`exclude` - включить/исключить значения (регулярки, массивы)
- `missing` - значение для документов без поля

*Примеры:*

    ```python
    # Базовое использование
    Terms(field="category", size=10, order={"_count": "desc"})

    # Топ-5 категорий по количеству товаров
    Terms(field="category", size=5, order={"_count": "desc"})

    # Группировка с фильтрацией значений
    Terms(field="brand", include=["apple", "samsung", "google"], min_doc_count=10)

    # Сортировка по среднему рейтингу из под-агрегации
    Terms(field="category", order={"avg_rating": "desc"})

    # С значением по умолчанию для отсутствующих полей
    Terms(field="optional_field", missing="N/A", size=20)
    ```

#### <a id="range-агрегация"></a>📈 Range - группировка по диапазонам

*Параметры:*
- `field` - числовое поле (обязательное)
- `ranges` - список диапазонов (обязательный)
- `keyed` - возвращать результаты как словарь с ключами (True/False)

*Примеры:*

    ```python
    # Базовое использование
    Range(
        field="price",
        ranges=[
            {"to": 100},
            {"from": 100, "to": 500},
            {"from": 500, "to": 1000},
            {"from": 1000}
        ]
    )

    # Группировка по ценовым диапазонам
    Range(
        field="price",
        ranges=[
            {"key": "cheap", "to": 50},
            {"key": "medium", "from": 50, "to": 200},
            {"key": "expensive", "from": 200}
        ],
        keyed=True
    )

    # Возрастные группы
    Range(
        field="age",
        ranges=[
            {"to": 18},
            {"from": 18, "to": 30},
            {"from": 30, "to": 50},
            {"from": 50}
        ]
    )

    # Диапазоны рейтинга
    Range(
        field="rating",
        ranges=[
            {"key": "poor", "to": 2},
            {"key": "average", "from": 2, "to": 4},
            {"key": "good", "from": 4}
        ],
        keyed=True
    )
    ```

#### <a id="datehistogram"></a>📅 DateHistogram - группировка по времени

*Интервалы:*
- `calendar_interval`: `"minute"`, `"hour"`, `"day"`, `"week"`, `"month"`, `"quarter"`, `"year"`
- `fixed_interval`: `"1d"` (1 день), `"2w"` (2 недели), `"30d"`, `"1M"` (1 месяц)

*Параметры:*
- `format` - формат даты для ключей (`"yyyy-MM-dd"`, `"yyyy-MM"`)
- `time_zone` - временная зона (`"UTC"`, `"Europe/Moscow"`)
- `min_doc_count` - минимальное количество документов в группе
- `extended_bounds` - расширить границы гистограммы

*Примеры:*

    ```python
    # Базовое использование
    DateHistogram(
        field="created_at",
        calendar_interval="month",
        format="yyyy-MM",
        time_zone="UTC"
    )

    # Продажи по месяцам
    DateHistogram(
        field="order_date",
        calendar_interval="month",
        format="yyyy-MM",
        time_zone="Europe/Moscow"
    )

    # Активность по часам
    DateHistogram(
        field="timestamp",
        calendar_interval="hour",
        format="HH:mm",
        time_zone="UTC",
        min_doc_count=0
    )

    # Еженедельная статистика
    DateHistogram(
        field="event_time",
        calendar_interval="week",
        format="yyyy-MM-dd",
        time_zone="UTC",
        extended_bounds={
            "min": "2024-01-01",
            "max": "2024-12-31"
        }
    )
    ```

#### <a id="daterange"></a>📆 DateRange - диапазоны дат

*Параметры:*
- `field` - поле с датой (обязательное)
- `ranges` - список диапазонов дат (обязательный)
- `format` - формат даты
- `time_zone` - временная зона

*Примеры:*

    ```python
    # Базовое использование
    DateRange(
        field="order_date",
        ranges=[
            {"to": "2024-01-01"},
            {"from": "2024-01-01", "to": "2024-02-01"},
            {"from": "2024-02-01"}
        ],
        format="yyyy-MM-dd"
    )

    # Группировка по кварталам
    DateRange(
        field="created_at",
        ranges=[
            {"key": "Q1", "from": "2024-01-01", "to": "2024-04-01"},
            {"key": "Q2", "from": "2024-04-01", "to": "2024-07-01"},
            {"key": "Q3", "from": "2024-07-01", "to": "2024-10-01"},
            {"key": "Q4", "from": "2024-10-01", "to": "2025-01-01"}
        ],
        format="yyyy-MM-dd",
        keyed=True
    )

    # Периоды активности
    DateRange(
        field="activity_date",
        ranges=[
            {"key": "today", "from": "now/d", "to": "now+1d/d"},
            {"key": "week", "from": "now-7d/d", "to": "now/d"},
            {"key": "month", "from": "now-30d/d", "to": "now/d"}
        ]
    )
    ```

#### <a id="histogram"></a>📐 Histogram - числовые интервалы

*Параметры:*
- `field` - числовое поле (обязательное)
- `interval` - размер интервала (обязательный)
- `min_doc_count` - минимальное количество документов в группе
- `extended_bounds` - расширить границы гистограммы
- `order` - сортировка групп

*Примеры:*

    ```python
    # Базовое использование
    Histogram(
        field="price",
        interval=100,
        extended_bounds={"min": 0, "max": 1000}
    )

    # Цены с интервалом 50
    Histogram(
        field="price",
        interval=50,
        min_doc_count=1,
        extended_bounds={"min": 0, "max": 500}
    )

    # Оценки с интервалом 0.5
    Histogram(
        field="rating",
        interval=0.5,
        extended_bounds={"min": 1.0, "max": 5.0}
    )

    # Возраст с интервалом 5 лет
    Histogram(
        field="age",
        interval=5,
        min_doc_count=0,
        order={"_key": "asc"}
    )
    ```

#### <a id="geohashgrid"></a>🌍 GeoHashGrid - географическая сетка

*Параметры:*
- `field` - поле с геоданными (обязательное)
- `precision` - точность геохэша (1-12)
- `size` - количество возвращаемых ячеек
- `shard_size` - размер на шарде

*Примеры:*

    ```python
    # Базовое использование
    GeoHashGrid(
        field="location",
        precision=5
    )

    # Группировка по географическим регионам
    GeoHashGrid(
        field="coordinates",
        precision=4,  # ~39km x 19.5km на экваторе
        size=100
    )

    # Более детальная сетка
    GeoHashGrid(
        field="location",
        precision=7,  # ~153m x 153m на экваторе
        size=1000
    )

    # С настройками производительности
    GeoHashGrid(
        field="geo_point",
        precision=6,
        size=500,
        shard_size=1000
    )
    ```

#### <a id="nested-агрегация"></a>🏗️ Nested - вложенные агрегации

*Логика работы:*
Nested агрегации позволяют считать статистику ПО ВЛОЖЕННЫМ ОБЪЕКТАМ отдельно от основного документа. Агрегация работает со ВСЕМИ вложенными объектами ВСЕХ документов, которые попадают в результаты запроса.

*Примеры:*

    ```python
    # Базовое использование
    # Создание nested агрегации
    nested_agg = Nested(path="variants")

    # Добавление агрегаций внутрь nested
    filter_agg = Filter(filter=Range(variants__stock={"gt": 0}))
    filter_agg.bucket("colors", Terms(field="variants.color", size=3))
    filter_agg.metric("price_stats", Stats(field="variants.price_modifier"))

    nested_agg.bucket("available_variants", filter_agg)

    # Анализ вложенных тегов
    Nested(path="tags").bucket(
        "popular_tags",
        Terms(field="tags.name", size=10)
    ).metric(
        "avg_priority",
        Avg(field="tags.priority")
    )

    # Вложенные отзывы
    Nested(path="reviews").bucket(
        "rating_distribution",
        Range(
            field="reviews.rating",
            ranges=[
                {"to": 2},
                {"from": 2, "to": 4},
                {"from": 4}
            ]
        )
    ).metric(
        "total_reviews",
        ValueCount(field="reviews.id")
    )
    ```

#### <a id="reversenested"></a>↩️ ReverseNested - обратные вложенные

*Применение:* Возврат из nested агрегации к корневому документу

*Примеры:*

    ```python
    # Базовое использование
    Nested(path="variants").bucket(
        "colors",
        Terms(field="variants.color")
    ).bucket(
        "back_to_root",
        ReverseNested().bucket(
            "categories",
            Terms(field="category")
        )
    )

    # Анализ: для каждого цвета вариантов - какие категории товаров
    Nested(path="variants").bucket(
        "color_groups",
        Terms(field="variants.color", size=5)
    ).bucket(
        "product_categories",
        ReverseNested().bucket(
            "categories",
            Terms(field="category", size=3)
        )
    )

    # Вложенные теги -> категории товаров
    Nested(path="tags").bucket(
        "tag_usage",
        Terms(field="tags.name", size=10)
    ).bucket(
        "tagged_products",
        ReverseNested().bucket(
            "product_types",
            Terms(field="type", size=5)
        )
    )
    ```

#### <a id="filter-агрегация"></a>🔍 Filter - агрегации с фильтром

*Параметры:*
- `filter` - запрос для фильтрации документов (обязательный)

*Примеры:*

    ```python
    # Базовое использование
    Filter(
        filter=Term(is_on_sale=True)
    ).bucket("categories", Terms(field="category"))

    # Агрегации только для активных пользователей
    Filter(
        filter=Term(is_active=True)
    ).bucket(
        "age_groups",
        Range(
            field="age",
            ranges=[
                {"to": 18},
                {"from": 18, "to": 30},
                {"from": 30, "to": 50},
                {"from": 50}
            ]
        )
    )

    # Комбинированный фильтр
    Filter(
        filter=Bool(
            must=[
                Range(price={"gte": 100}),
                Term(in_stock=True)
            ]
        )
    ).metric("total_value", Sum(field="price"))

    # Фильтр по дате
    Filter(
        filter=Range(
            created_at={
                "gte": "2024-01-01",
                "lt": "2024-02-01"
            }
        )
    ).bucket(
        "monthly_stats",
        DateHistogram(
            field="created_at",
            calendar_interval="day"
        )
    )
    ```

### <a id="метрические-агрегации-вычисления"></a>Метрические агрегации (вычисления)

#### <a id="stats"></a>📈 Stats - базовая статистика

*Возвращает:* `count`, `min`, `max`, `avg`, `sum`

*Параметры:*
- `field` - числовое поле (обязательное)
- `missing` - значение для документов без поля
- `sigma` - настройки для расширенной статистики

*Примеры:*

    ```python
    # Базовое использование
    Stats(field="price")

    # Базовая статистика по цене
    Stats(field="price")

    # Статистика с значением по умолчанию
    Stats(field="rating", missing=0)

    # Статистика по нескольким полям
    Stats(field="price", sigma=2)
    Stats(field="quantity", missing=1)
    ```

#### <a id="extendedstats"></a>📊 ExtendedStats - расширенная статистика

*Возвращает:* `count`, `min`, `max`, `avg`, `sum`, `sum_of_squares`, `variance`, `std_deviation`, `std_deviation_bounds`

*Параметры:*
- `field` - числовое поле (обязательное)
- `sigma` - количество стандартных отклонений для границ (по умолчанию 2)
- `missing` - значение для документов без поля

*Примеры:*

    ```python
    # Базовое использование
    ExtendedStats(field="price", sigma=2)

    # Расширенная статистика с 3 сигма
    ExtendedStats(field="price", sigma=3)

    # Анализ распределения оценок
    ExtendedStats(field="rating")

    # Статистика с значением по умолчанию
    ExtendedStats(field="response_time", missing=0, sigma=2)
    ```

#### <a id="avg"></a>➗ Avg - среднее значение

*Параметры:*
- `field` - числовое поле (обязательное)
- `missing` - значение для документов без поля
- `script` - скрипт для вычисления значения

*Примеры:*

    ```python
    # Базовое использование
    Avg(field="rating")

    # Средний рейтинг
    Avg(field="rating")

    # Средняя цена со значением по умолчанию
    Avg(field="price", missing=0)

    # Среднее время выполнения
    Avg(field="execution_time_ms")

    # С использованием скрипта
    Avg(script={"source": "doc['price'].value * params.tax", "params": {"tax": 1.2}})
    ```

#### <a id="sum"></a>➕ Sum - сумма

*Параметры:*
- `field` - числовое поле (обязательное)
- `missing` - значение для документов без поля
- `script` - скрипт для вычисления значения

*Примеры:*

    ```python
    # Базовое использование
    Sum(field="quantity")

    # Общее количество товаров
    Sum(field="stock")

    # Сумма продаж
    Sum(field="total_amount")

    # Сумма с значением по умолчанию
    Sum(field="revenue", missing=0)

    # Сумма через скрипт
    Sum(script={"source": "doc['price'].value * doc['quantity'].value"})
    ```

#### <a id="min"></a>📉 Min - минимум

*Параметры:*
- `field` - числовое поле (обязательное)
- `missing` - значение для документов без поля
- `script` - скрипт для вычисления значения

*Примеры:*

    ```python
    # Базовое использование
    Min(field="price")

    # Минимальная цена
    Min(field="price")

    # Самый ранний заказ
    Min(field="order_date")

    # Минимальный возраст
    Min(field="age")

    # Минимальное значение через скрипт
    Min(script={"source": "Math.min(doc['price'].value, doc['discount_price'].value)"})
    ```

#### <a id="max"></a>📈 Max - максимум

*Параметры:*
- `field` - числовое поле (обязательное)
- `missing` - значение для документов без поля
- `script` - скрипт для вычисления значения

*Примеры:*

    ```python
    # Базовое использование
    Max(field="score")

    # Максимальный рейтинг
    Max(field="rating")

    # Последняя дата обновления
    Max(field="updated_at")

    # Максимальная температура
    Max(field="temperature")

    # Максимальное значение через скрипт
    Max(script={"source": "Math.max(doc['score1'].value, doc['score2'].value)"})
    ```

#### <a id="cardinality"></a>🔢 Cardinality - уникальные значения

*Параметры:*
- `field` - поле для подсчета уникальных значений (обязательное)
- `precision_threshold` - точность подсчета (по умолчанию 3000)
- `missing` - значение для документов без поля

*Применение:* Подсчет уникальных пользователей, IP-адресов и т.д.

*Примеры:*

    ```python
    # Базовое использование
    Cardinality(field="user_id")

    # Количество уникальных пользователей
    Cardinality(field="user_id")

    # Количество уникальных городов с повышенной точностью
    Cardinality(field="city", precision_threshold=10000)

    # Уникальные сессии
    Cardinality(field="session_id")

    # Уникальные IP-адреса
    Cardinality(field="ip_address", precision_threshold=50000)
    ```

#### <a id="valuecount"></a>🔢 ValueCount - подсчет всех значений

*Параметры:*
- `field` - поле для подсчета (обязательное)

*Отличие от Cardinality:* ValueCount считает ВСЕ значения (включая дубли), Cardinality - только уникальные

*Примеры:*

    ```python
    # Базовое использование
    ValueCount(field="tags")

    # Общее количество тегов
    ValueCount(field="tags")

    # Количество оценок
    ValueCount(field="rating")

    # Количество заказов
    ValueCount(field="order_id")

    # Количество просмотров
    ValueCount(field="view_count")
    ```

#### <a id="percentiles"></a>📊 Percentiles - процентили

*Параметры:*
- `field` - числовое поле (обязательное)
- `percents` - список процентилей (по умолчанию [1, 5, 25, 50, 75, 95, 99])
- `missing` - значение для документов без поля
- `tdigest` - настройки алгоритма

*Примеры:*

    ```python
    # Базовое использование
    Percentiles(field="response_time", percents=[95, 99, 99.9])

    # 95-й и 99-й процентили времени ответа
    Percentiles(field="response_time_ms", percents=[95, 99])

    # Процентили цены
    Percentiles(field="price", percents=[25, 50, 75, 90])

    # Процентили с настройками
    Percentiles(
        field="load_time",
        percents=[50, 75, 90, 95, 99],
        missing=0,
        tdigest={"compression": 100}
    )
    ```

#### <a id="percentileranks"></a>🏆 PercentileRanks - ранги процентилей

*Параметры:*
- `field` - числовое поле (обязательное)
- `values` - значения для которых вычисляются ранги (обязательные)
- `missing` - значение для документов без поля

*Логика:* Процент документов со значением МЕНЬШЕ или РАВНЫМ указанному

*Примеры:*

    ```python
    # Базовое использование
    PercentileRanks(field="load_time", values=[100, 200])

    # Какой процент загрузок быстрее 100мс и 200мс
    PercentileRanks(field="load_time_ms", values=[100, 200])

    # Процент товаров дешевле указанных цен
    PercentileRanks(field="price", values=[50, 100, 200])

    # Ранги времени ответа
    PercentileRanks(
        field="response_time",
        values=[100, 250, 500, 1000],
        missing=0
    )
    ```

### <a id="конвейерные-агрегации"></a>Конвейерные агрегации

#### <a id="avgbucket"></a>➗ AvgBucket - среднее по группам

*Параметры:*
- `buckets_path` - путь к агрегации (обязательный)
- `gap_policy` - политика для пропусков: `"skip"`, `"insert_zeros"`, `"keep_values"`

*Примеры:*

    ```python
    # Базовое использование
    AvgBucket(buckets_path="sales_per_month>total_sales")

    # Среднемесячные продажи
    DateHistogram(
        field="order_date",
        calendar_interval="month"
    ).metric(
        "total_sales",
        Sum(field="amount")
    ).pipeline(
        "avg_monthly_sales",
        AvgBucket(buckets_path="total_sales")
    )

    # Среднее по категориям
    Terms(
        field="category"
    ).metric(
        "category_sales",
        Sum(field="sales")
    ).pipeline(
        "avg_category_sales",
        AvgBucket(buckets_path="category_sales")
    )
    ```

#### <a id="sumbucket"></a>➕ SumBucket - сумма по группам

*Параметры:*
- `buckets_path` - путь к агрегации (обязательный)
- `gap_policy` - политика для пропусков

*Примеры:*

    ```python
    # Базовое использование
    SumBucket(buckets_path="daily>total")

    # Сумма дневных продаж за месяц
    DateHistogram(
        field="order_date",
        calendar_interval="day"
    ).metric(
        "daily_total",
        Sum(field="amount")
    ).pipeline(
        "monthly_total",
        SumBucket(buckets_path="daily_total")
    )

    # Общая сумма по всем категориям
    Terms(
        field="department"
    ).metric(
        "dept_expenses",
        Sum(field="expense")
    ).pipeline(
        "total_expenses",
        SumBucket(buckets_path="dept_expenses")
    )
    ```

#### <a id="minbucket"></a>📉 MinBucket - минимум по группам

*Параметры:*
- `buckets_path` - путь к агрегации (обязательный)
- `gap_policy` - политика для пропусков

*Примеры:*

    ```python
    # Базовое использование
    MinBucket(buckets_path="temperature_by_hour>min_temp")

    # Минимальная дневная температура за месяц
    DateHistogram(
        field="timestamp",
        calendar_interval="day"
    ).metric(
        "min_daily_temp",
        Min(field="temperature")
    ).pipeline(
        "min_monthly_temp",
        MinBucket(buckets_path="min_daily_temp")
    )

    # Минимальные продажи по категориям
    Terms(
        field="product_type"
    ).metric(
        "type_sales",
        Sum(field="sales")
    ).pipeline(
        "min_type_sales",
        MinBucket(buckets_path="type_sales")
    )
    ```

#### <a id="maxbucket"></a>📈 MaxBucket - максимум по группам

*Параметры:*
- `buckets_path` - путь к агрегации (обязательный)
- `gap_policy` - политика для пропусков

*Примеры:*

    ```python
    # Базовое использование
    MaxBucket(buckets_path="sales_by_category>max_sales")

    # Максимальные продажи по категориям
    Terms(
        field="category"
    ).metric(
        "category_sales",
        Sum(field="amount")
    ).pipeline(
        "max_category_sales",
        MaxBucket(buckets_path="category_sales")
    )

    # Максимальная дневная активность
    DateHistogram(
        field="date",
        calendar_interval="day"
    ).metric(
        "daily_users",
        Cardinality(field="user_id")
    ).pipeline(
        "max_daily_users",
        MaxBucket(buckets_path="daily_users")
    )
    ```

#### <a id="statsbucket"></a>📊 StatsBucket - статистика по группам

*Параметры:*
- `buckets_path` - путь к агрегации (обязательный)
- `gap_policy` - политика для пропусков

*Примеры:*

    ```python
    # Базовое использование
    StatsBucket(buckets_path="monthly>total")

    # Статистика по месячным продажам
    DateHistogram(
        field="order_date",
        calendar_interval="month"
    ).metric(
        "monthly_sales",
        Sum(field="amount")
    ).pipeline(
        "sales_stats",
        StatsBucket(buckets_path="monthly_sales")
    )

    # Статистика по категориям
    Terms(
        field="region"
    ).metric(
        "region_revenue",
        Sum(field="revenue")
    ).pipeline(
        "revenue_stats",
        StatsBucket(buckets_path="region_revenue")
    )
    ```

#### <a id="cumulativesum"></a>🧮 CumulativeSum - накопительная сумма

*Параметры:*
- `buckets_path` - путь к агрегации (обязательный)
- `format` - формат вывода

*Примеры:*

    ```python
    # Базовое использование
    CumulativeSum(buckets_path="daily>total")

    # Накопительные продажи за месяц
    DateHistogram(
        field="order_date",
        calendar_interval="day"
    ).metric(
        "daily_sales",
        Sum(field="amount")
    ).pipeline(
        "cumulative_sales",
        CumulativeSum(buckets_path="daily_sales")
    )

    # Накопительные пользователи
    DateHistogram(
        field="signup_date",
        calendar_interval="week"
    ).metric(
        "weekly_signups",
        ValueCount(field="user_id")
    ).pipeline(
        "total_signups",
        CumulativeSum(buckets_path="weekly_signups")
    )
    ```

#### <a id="derivative"></a>📈 Derivative - изменение между группами

*Параметры:*
- `buckets_path` - путь к агрегации (обязательный)
- `gap_policy` - политика для пропусков
- `unit` - единица измерения (для дат)

*Примеры:*

    ```python
    # Базовое использование
    Derivative(buckets_path="monthly>total")

    # Изменение месячных продаж
    DateHistogram(
        field="order_date",
        calendar_interval="month"
    ).metric(
        "monthly_sales",
        Sum(field="amount")
    ).pipeline(
        "sales_change",
        Derivative(buckets_path="monthly_sales")
    )

    # Изменение температуры по дням
    DateHistogram(
        field="date",
        calendar_interval="day"
    ).metric(
        "avg_temp",
        Avg(field="temperature")
    ).pipeline(
        "temp_change",
        Derivative(buckets_path="avg_temp")
    )
    ```

#### <a id="movingavg"></a>📉 MovingAvg - скользящее среднее

*Модели:*
- `simple` - простое скользящее среднее
- `linear` - линейное взвешенное
- `ewma` - экспоненциальное взвешенное
- `holt` - двойное экспоненциальное
- `holt_winters` - тройное экспоненциальное

*Параметры:*
- `buckets_path` - путь к агрегации (обязательный)
- `window` - размер окна
- `model` - модель расчета
- `gap_policy` - политика для пропусков

*Примеры:*

    ```python
    # Базовое использование
    MovingAvg(
        buckets_path="daily>total",
        model="simple",
        window=7
    )

    # 7-дневное скользящее среднее продаж
    DateHistogram(
        field="order_date",
        calendar_interval="day"
    ).metric(
        "daily_sales",
        Sum(field="amount")
    ).pipeline(
        "moving_avg_7d",
        MovingAvg(buckets_path="daily_sales", model="simple", window=7)
    )

    # Экспоненциальное скользящее среднее
    DateHistogram(
        field="timestamp",
        calendar_interval="hour"
    ).metric(
        "hourly_requests",
        ValueCount(field="request_id")
    ).pipeline(
        "ewma_24h",
        MovingAvg(buckets_path="hourly_requests", model="ewma", window=24)
    )
    ```
---
## <a id="построение-запросов"></a>Построение запросов

*Примеры:*

    ```python
    # Базовый синтаксис
    from elasticsearch.dsl import Search
    from elasticsearch.dsl.query import Match, Range, Term
    from elasticsearch.dsl.aggs import Terms, Stats

    # Создание запроса
    search = Search()

    # Добавление запроса
    search = search.query(Match(title="smartphone"))

    # Добавление фильтров
    search = search.filter(Range(price={"gte": 100}))
    search = search.filter(Term(is_available=True))

    # Добавление агрегаций
    search.aggs.bucket("categories", Terms(field="category", size=10))
    search.aggs.metric("price_stats", Stats(field="price"))

    # Настройка вывода
    search = search[:20]                          # Пагинация
    search = search.sort("-rating", "price")      # Сортировка
    search = search.source(includes=["id", "title", "price"])  # Выбор полей

    # Вариант 1: Преобразование в словарь для стандартного клиента
    from elasticsearch import Elasticsearch
    es = Elasticsearch()
    query_dict = search.to_dict()
    result = es.search(index="products", body=query_dict)

    # Вариант 2: Выполнение через Search (возвращает Response объект)
    response = search.using(es).index("products").execute()

    # Работа с результатом как с объектом
    print(f"Найдено: {response.hits.total.value}")
    for hit in response.hits:
        print(f"ID: {hit.id}, Score: {hit.meta.score}")
        print(f"Данные: {hit.title} - {hit.price}")
    ```

*Цепочка вызовов:*

    ```python
    search = (
        Search()
        .query(Match(title="phone"))
        .filter(Range(price={"gte": 100, "lte": 1000}))
        .filter(Term(is_available=True))
        .aggs.bucket("brands", Terms(field="brand", size=5))
        .aggs.metric("stats", Stats(field="price"))
        .sort("-rating", "price")
        .source(includes=["id", "title", "price", "rating"])
        [:10]
    )
    ```

*Только агрегации (без документов):*

    ```python
    search = Search()[:0]  # или .extra(size=0)
    search.aggs.bucket("categories", Terms(field="category"))
    ```

*Пагинация и сортировка:*

    ```python
    # Базовая пагинация
    search = search[0:10]        # первые 10 документов
    search = search[10:20]       # документы 11-20

    # Через параметры (альтернатива)
    search = search.extra(from=0, size=10)

    # Сортировка
    search = search.sort("price")           # по возрастанию цены
    search = search.sort("-price")          # по убыванию цены
    search = search.sort("price", "-rating") # сначала по цене, потом по рейтингу

    # По релевантности (по умолчанию)
    search = search.sort("_score")

    # По нескольким полям с разными порядками
    search = search.sort(
        {"price": {"order": "asc"}},
        {"rating": {"order": "desc", "missing": "_last"}}
    )
    ```

*Пагинация через search_after (для глубокой пагинации):*

    ```python
    # Первый запрос
    first_page = (
        Search()
        .query(Match(title="phone"))
        .sort("_id")  # Обязательно нужен уникальный ключ сортировки
        [:10]
    )
    response = first_page.execute()

    # Следующая страница (используем последний документ)
    last_hit = response.hits[-1]
    next_page = (
        Search()
        .query(Match(title="phone"))
        .sort("_id")
        .extra(search_after=[last_hit.id])
        [:10]
    )
    ```

*Сложные nested агрегации:*

    ```python
    search = (
        Search()[:0]
        .aggs.bucket("variants_analysis",
            Nested(path="variants")
            .bucket("in_stock",
                Filter(filter=Range(variants__stock={"gt": 0}))
                .bucket("colors", Terms(field="variants.color", size=5))
                .metric("modifier_stats", Stats(field="variants.price_modifier"))
            )
        )
    )
    ```
---
## <a id="полезные-советы"></a>Полезные советы

*Когда использовать `.query()` vs `.filter()`:*
- **`.query()`** - для полнотекстового поиска, влияет на релевантность (score)
- **`.filter()`** - для точных совпадений, не влияет на score, кэшируется Elasticsearch

*Имена полей в nested объектах:*

    ```python
    # Правильно (двойное подчеркивание для запросов)
    Term(variants__color="black")
    Range(variants__stock={"gt": 0})

    # Для агрегаций (точка)
    Terms(field="variants.color")
    ```

*Операторы Python для запросов:*

    ```python
    q1 = Match(title="phone")
    q2 = Range(price={"lte": 1000})

    Search().query(q1 & q2)   # И (AND) - оба должны выполняться
    Search().query(q1 | q2)   # ИЛИ (OR) - хотя бы один
    Search().query(~q1)       # НЕ (NOT) - исключить
    ```
---
## <a id="частые-ошибки"></a>Частые ошибки

*1. Term для текстовых полей без .keyword:*

    ```python
    # ❌ Неправильно (поле text проанализировано на токены)
    Term(description="wireless")  # Ищет токен "wireless", а не строку

    # ✅ Правильно (использовать .keyword для точного совпадения)
    Term(description__keyword="Wireless Headphones")
    ```

*2. Поле может отсутствовать у некоторых документов:*

    ```python
    # Добавить значение по умолчанию
    Terms(field="optional_field", missing="N/A")
    Stats(field="price", missing=0)
    ```

*3. Слишком много уникальных значений в агрегации:*

    ```python
    # Ограничить размер возвращаемых групп
    Terms(field="tags", size=100)  # вместо дефолтных 10
    Terms(field="user_id", size=1000, execution_hint="map")
    ```

*4. Забыли преобразовать Search в словарь:*

    ```python
    from elasticsearch import Elasticsearch
    es = Elasticsearch()

    # ❌ Неправильно (передаем объект Search)
    result = es.search(index="products", body=search)

    # ✅ Правильно (преобразуем в dict)
    result = es.search(index="products", body=search.to_dict())

    # ✅ Или используем execute() через Search
    response = search.using(es).index("products").execute()
    ```

*5. Не указан индекс при использовании execute():*

    ```python
    # ❌ Неправильно
    search = Search().query(Match(title="test"))
    response = search.using(es).execute()  # Ошибка: нет индекса

    # ✅ Правильно
    response = search.using(es).index("products").execute()
    ```