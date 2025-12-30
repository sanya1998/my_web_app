from typing import List

from es.schemas.products import Brand, ProductReadSchema
from pydantic import BaseModel


class ProductResponse(ProductReadSchema):
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

    brands: List[Brand]
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
