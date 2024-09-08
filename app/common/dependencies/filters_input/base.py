from typing import Any

from app.config.main import settings
from fastapi import Query
from pydantic import BaseModel, computed_field


class BaseFiltersInput(BaseModel):
    # Здесь указываются типы переменных и значения по умолчанию
    limit: int = Query(default=settings.LIMIT_DEFAULT, ge=1, le=settings.LIMIT_MAX)
    offset: int = Query(default=settings.OFFSET_DEFAULT, ge=0)

    @computed_field
    @property
    def pagination(self) -> tuple[int, int] | None:
        return self.limit, self.offset

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        model_dict = super().model_dump(*args, **kwargs)
        sorted_dict = dict(
            {k: v for k, v in model_dict.items() if k.startswith("join_")},
            **{k: v for k, v in model_dict.items() if not k.startswith("join_")}
        )

        return sorted_dict

    class Config:
        use_enum_values = True
