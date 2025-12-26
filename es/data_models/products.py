from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, computed_field


class Category(str, Enum):
    SMARTPHONE = "smartphone"
    LAPTOP = "laptop"
    TABLET = "tablet"
    HEADPHONES = "headphones"
    SMARTWATCH = "smartwatch"
    CAMERA = "camera"


class VariantIn(BaseModel):
    """Вариант товара для записи (без вычисляемых полей)"""

    color: str
    size: str = Field(default="standard")
    price_modifier: float = Field(default=0.0)
    stock: int = Field(default=0)
    sku: Optional[str] = None


class ProductCreateIn(BaseModel):
    """Модель товара для записи в Elasticsearch"""

    # Основная информация
    id: str
    product_name: str
    category: Category
    brand: str
    base_price: float

    # Общая информация
    rating: float
    description: str
    search_content: str
    specifications: Dict[str, Any]
    features: List[str]
    is_available: bool
    is_on_sale: bool
    created_date: date
    tags: List[str]

    # Варианты товара
    variants: List[VariantIn] = []


class ProductUpdateIn(BaseModel):
    """Модель товара для записи в Elasticsearch"""

    # Основная информация
    id: str
    product_name: str
    category: Category
    brand: str
    base_price: float

    # Общая информация
    rating: float
    description: str
    search_content: str
    specifications: Dict[str, Any]
    features: List[str]
    is_available: bool
    is_on_sale: bool
    tags: List[str]

    # Варианты товара
    variants: List[VariantIn] = []


class ProductOut(ProductCreateIn):
    """Модель товара для чтения из Elasticsearch (с вычисляемыми полями)"""

    # Вычисляемые поля из Elasticsearch runtime fields
    total_stock: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    available_colors: Optional[List[str]] = None

    @computed_field
    @property
    def price_range(self) -> str:
        """Диапазон цен для отображения (вычисляется локально)"""
        if self.min_price and self.max_price:
            if self.min_price == self.max_price:
                return f"${self.min_price:.2f}"
            return f"${self.min_price:.2f} - ${self.max_price:.2f}"
        return f"${self.base_price:.2f}"

    @computed_field
    @property
    def has_variants(self) -> bool:
        """Есть ли варианты у товара"""
        return len(self.variants) > 0
