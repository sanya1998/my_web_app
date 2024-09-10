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

    class Config:
        use_enum_values = True
