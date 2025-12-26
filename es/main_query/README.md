Для MainQuery.aggs:
```
Aggregation                           # Корень всех агрегаций
│
├── FieldAgg                          # Агрегации, работающие с полями
│   ├── TermsAgg                      # 📊 Группировка по категориям, тегам, брендам
│   ├── RangeAgg                      # 📈 Диапазоны цен, рейтингов, дат
│   ├── DateHistogramAgg              # 📅 Группировка по времени (дни, недели, месяцы)
│   ├── StatsAgg                      # 📐 Базовая статистика: min, max, avg, sum
│   ├── CardinalityAgg                # 🔢 Приблизительный подсчет уникальных значений
│   └── ValueCountAgg                 # 🔢 Точный подсчет всех значений
│
├── FilterAgg                         # 🔍 Агрегация по отфильтрованным документам
│
├── NestedAgg                         # 🗂️ Агрегации по вложенных объектам
│
├── GlobalAgg                         # 🌍 Глобальная агрегация по всем документам
│
└── PipelineAgg                       # 🚰 Конвейерные агрегации (над результатами других)
    ├── AvgBucketAgg                  # 📊 Среднее значение по бакетам
    ├── SumBucketAgg                  # ➕ Сумма по бакетам
    ├── MaxBucketAgg                  # ⬆️ Максимум по бакетам
    ├── MinBucketAgg                  # ⬇️ Минимум по бакетам
    ├── StatsBucketAgg                # 📈 Статистика по бакетам
    ├── DerivativeAgg                 # 📈 Производная по метрикам
    └── CumulativeSumAgg              # 📊 Кумулятивная сумма
```


Для MainQuery.query:
```
Query                           # Корень всех запросов.
├── MatchAll(Query)             # Получить все документы
├── FuzzySearch(Query)          # Нечеткий поиск - по смыслу, с анализом текста
│   ├── SingleFuzzy(FuzzySearch)    # К одному полю - query + field
│   │   ├── Match(SingleFuzzy)      # Обычный текстовый поиск
│   │   └── MatchPhrase(SingleFuzzy) # Поиск точной фразы
│   └── MultiFuzzy(FuzzySearch)     # К нескольким полям - query + fields
│       ├── MultiMatch(MultiFuzzy)  # Поиск по нескольким полям
│       ├── QueryString(MultiFuzzy) # Расширенный синтаксис запросов
│       └── SimpleQueryString(MultiFuzzy) # Упрощенный синтаксис
├── ExactSearch(Query)          # Точный поиск - фильтрация по точным значениям
│   ├── Term(ExactSearch)       # Точное совпадение - field + value
│   ├── Terms(ExactSearch)      # Совпадение с любым из значений - field + values
│   ├── Range(ExactSearch)      # Диапазон значений - field + gte/gt/lte/lt
│   └── Exists(ExactSearch)     # Проверка существования поля - field
├── Clause(Query)               # Логические условия - список запросов
│   ├── Must(Clause)            # Обязательные условия - ДОЛЖНЫ выполняться
│   ├── Filter(Clause)          # Фильтры - ДОЛЖНЫ выполняться (без влияния на релевантность)
│   ├── MustNot(Clause)         # Запрещенные условия - НЕ ДОЛЖНЫ выполняться
│   ├── Should(Clause)          # Желательные условия - ЖЕЛАТЕЛЬНЫ для выполнения
│   └── Bool(Query)             # Полноценный булев запрос - комбинация всех условий
└── NestedQuery(Query)          # Запрос для поиска внутри вложенных объектов
```