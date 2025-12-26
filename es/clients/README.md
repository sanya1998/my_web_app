```
clients/
├── models/           # Модели данных (Pydantic, dataclasses)
│   ├── aliases.py    # AliasInfo, AddAlias, RemoveAlias, AliasesBody
│   ├── config.py     # IndexConfig
│   ├── document.py   # OperationType, QueryOperationType, RefreshType
│   └── pydantic.py   # DocumentResult, SearchResult
├── base.py           # BaseESClient
├── index.py          # IndexClient
└── pydantic_.py      # PydanticESClient
```