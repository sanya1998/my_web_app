from datetime import date
from typing import Any, Dict, List, Optional

from es.schemas.products import Brand, Category, Color, Feature, Size, SpecKey, VariantIn
from pydantic import BaseModel, Field


class VariantInput(BaseModel):
    """Модель для варианта товара (если нужно локально)"""

    color: Color
    size: Size = Field(default=Size.STANDARD)
    price_modifier: float = Field(default=0.0)
    stock: int = Field(default=0)
    sku: Optional[str] = None


class ProductCreateInput(BaseModel):
    """Модель для создания товара"""

    id: str
    product_name: str
    category: Category
    brand: Brand
    base_price: float = Field(gt=0, description="Цена должна быть положительной")
    rating: float = Field(ge=0, le=5, description="Рейтинг от 0 до 5")
    description: str
    specifications: Dict[SpecKey, Any]
    features: List[Feature]
    is_available: bool = True
    is_on_sale: bool = False
    created_date: date = Field(default_factory=date.today, description="Дата создания")
    tags: List[str] = Field(default_factory=list)
    variants: List[VariantIn] = Field(default_factory=list, description="Варианты товара")


class ProductUpdateInput(BaseModel):
    """Модель для обновления товара"""

    product_name: Optional[str] = None
    category: Optional[Category] = None
    brand: Optional[Brand] = None
    base_price: Optional[float] = Field(None, gt=0)
    rating: Optional[float] = Field(None, ge=0, le=5)
    description: Optional[str] = None
    specifications: Optional[Dict[SpecKey, Any]] = None
    features: Optional[List[Feature]] = None
    is_available: Optional[bool] = None
    is_on_sale: Optional[bool] = None
    tags: Optional[List[str]] = None
    variants: Optional[List[VariantIn]] = None
