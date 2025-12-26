from datetime import date
from typing import Any, Dict, List, Optional

from es.data_models.products import Category, ProductOut, VariantIn
from pydantic import BaseModel, Field


# ============ RESPONSE MODELS ============
class ProductResponse(ProductOut):
    """Модель ответа для одного товара"""

    pass


class ProductsListResponse(BaseModel):
    """Модель ответа для списка товаров"""

    products: List[ProductResponse]
    # TODO:
    # total: int
    # page: int
    # per_page: int
    # total_pages: int


class BrandsResponse(BaseModel):
    """Модель ответа для списка брендов"""

    brands: List[str]
    total: int


class ProductCreateResponse(BaseModel):
    """Модель ответа при создании товара"""

    id: str
    message: str = "Product created successfully"


class ProductUpdateResponse(BaseModel):
    """Модель ответа при обновлении товара"""

    message: str = "Product updated successfully"


class ProductDeleteResponse(BaseModel):
    """Модель ответа при удалении товара"""

    message: str = "Product deleted successfully"
    doc: List[BaseModel]  # TODO: подумать, что сюда лучше


# ============ REQUEST MODELS ============
# TODO: много общих полей
class ProductCreate(BaseModel):
    """Модель для создания товара"""

    id: str
    product_name: str
    category: Category
    brand: str
    base_price: float = Field(gt=0, description="Цена должна быть положительной")
    rating: float = Field(ge=0, le=5, description="Рейтинг от 0 до 5")
    description: str
    search_content: str
    specifications: Dict[str, Any]
    features: List[str]
    is_available: bool = True
    is_on_sale: bool = False
    created_date: date = Field(default_factory=date.today, description="Дата создания")
    tags: List[str] = Field(default_factory=list)
    variants: List[VariantIn] = Field(default_factory=list, description="Варианты товара")


class ProductUpdate(BaseModel):
    """Модель для обновления товара"""

    product_name: Optional[str] = None
    category: Optional[Category] = None
    brand: Optional[str] = None
    base_price: Optional[float] = Field(None, gt=0)
    rating: Optional[float] = Field(None, ge=0, le=5)
    description: Optional[str] = None
    search_content: Optional[str] = None
    specifications: Optional[Dict[str, Any]] = None
    features: Optional[List[str]] = None
    is_available: Optional[bool] = None
    is_on_sale: Optional[bool] = None
    tags: Optional[List[str]] = None
