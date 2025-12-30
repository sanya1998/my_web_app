from enum import Enum
from typing import List, Optional

from es.schemas.products import Brand, Category, Color, Feature
from pydantic import BaseModel, ConfigDict, Field


class SortOrder(str, Enum):
    """Порядок сортировки"""

    ASC = "asc"
    DESC = "desc"


class SortField(str, Enum):
    """Поля для сортировки"""

    CREATED_DATE = "created_date"
    BASE_PRICE = "base_price"
    RATING = "rating"
    TOTAL_STOCK = "total_stock"


class ProductFilter(BaseModel):
    """Модель для фильтрации товаров"""

    # Текстовый поиск
    search_query: Optional[str] = Field(None, description="Поиск по всем текстовым полям")

    # Фильтрация по категории
    categories: Optional[List[Category]] = Field(None, description="Фильтр по категориям")

    # Фильтрация по бренду
    brands: Optional[List[Brand]] = Field(None, description="Фильтр по брендам")

    # Фильтрация по цене
    min_price: Optional[float] = Field(None, ge=0, description="Минимальная цена")
    max_price: Optional[float] = Field(None, ge=0, description="Максимальная цена")

    # Фильтрация по рейтингу
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Минимальный рейтинг")

    # Фильтрация по наличию
    is_available: Optional[bool] = Field(None, description="В наличии")
    is_on_sale: Optional[bool] = Field(None, description="Со скидкой")

    # Фильтрация по тегам
    tags: Optional[List[str]] = Field(None, description="Теги")

    # Фильтрация по фичам
    features: Optional[List[Feature]] = Field(None, description="Особенности/фичи")

    # Фильтрация по цветам (из вариантов)
    colors: Optional[List[Color]] = Field(None, description="Доступные цвета")


class ProductSort(BaseModel):
    """Модель для сортировки товаров"""

    sort_field: SortField = Field(SortField.CREATED_DATE, description="Поле для сортировки")
    order: SortOrder = Field(SortOrder.DESC, description="Порядок сортировки")


class PaginationParams(BaseModel):
    """Модель для пагинации"""

    page: int = Field(1, ge=1, description="Номер страницы")
    per_page: int = Field(10, ge=1, le=100, description="Количество элементов на странице")


class ProductCommonParams(ProductFilter, ProductSort, PaginationParams):
    """Объединенная модель для фильтрации, сортировки и пагинации"""

    model_config = ConfigDict(use_enum_values=True)
