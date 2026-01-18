from app.api.data.products.dependency import build_search_query, get_es_client, get_pydantic_es_client
from app.api.data.products.input import ProductCreateInput, ProductUpdateInput
from app.api.data.products.responses import (
    BrandsResponse,
    ProductDeleteResponse,
    ProductResponse,
    ProductsListResponse,
    ProductUpdateResponse,
)
from app.common.constants.paths import PRODUCTS_PATH
from app.common.constants.tags import TagsEnum
from app.common.helpers.api_version import VersionedAPIRouter
from app.config.common import settings
from app.consumers.es_write import ESMethod, Message
from elasticsearch import NotFoundError
from elasticsearch.dsl import AsyncSearch
from elasticsearch.dsl.aggs import Terms
from es.clients.pydantic_ import PydanticESClient
from es.constants import WRITE_SUFFIX
from es.schemas.products import Brand
from fastapi import Depends, HTTPException, status
from starlette.requests import Request

router = VersionedAPIRouter(prefix=PRODUCTS_PATH, tags=[TagsEnum.PRODUCTS])


# ============ CREATE ============
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Создать товар",
    description="Создание нового товара в Elasticsearch",
)
async def create_product(
    request: Request,
    product_data: ProductCreateInput,
):
    """
    Создание нового товара

    Args:
        request:
        product_data: Данные для создания товара
    Returns:
        ProductCreateResponse с ID созданного товара
    """
    try:
        m = Message(method=ESMethod.CREATE, kwargs=dict(document=product_data))
        await request.app.state.es_write_publisher.publish(m, exclude_unset=True)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating product: {str(e)}",
        )


# ============ READ (by ID) ============
@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Получить товар по ID",
    description="Получение товара по его уникальному идентификатору",
)
async def get_product(
    product_id: str,
    es_client: PydanticESClient = Depends(get_pydantic_es_client),
) -> ProductResponse:
    """
    Получение товара по ID

    Args:
        product_id: ID товара
        es_client: Клиент Elasticsearch

    Returns:
        ProductResponse с данными товара

    Raises:
        HTTPException 404: если товар не найден
    """
    try:
        product = await es_client.get(
            doc_id=product_id,
            response_model=ProductResponse,
        )
        return product

    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID '{product_id}' not found",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


# ============ READ (list with filters) ============
@router.get(
    "/",
    response_model=ProductsListResponse,
    summary="Получить список товаров",
    description="Получение списка товаров с фильтрацией, сортировкой и пагинацией",
)
async def get_products(
    main_query: AsyncSearch = Depends(build_search_query),
    es_client: PydanticESClient = Depends(get_pydantic_es_client),
) -> ProductsListResponse:
    """
    Получение списка товаров с фильтрами

    Args:
        main_query: объект AsyncSearch
        es_client: Клиент PydanticESClient

    Returns:
        ProductsListResponse со списком товаров и метаданными
    """
    try:
        result = await es_client.search(body=main_query.to_dict(), response_model=ProductResponse)
        return ProductsListResponse(products=result.sources)  # TODO: pycharm подчеркивает
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error searching products: {str(e)}")


@router.get(
    "/",
    response_model=ProductsListResponse,
    summary="Поиск товаров",
    description="Поиск товаров с использованием AsyncSearch DSL",
)
@router.set_api_version("v2")
async def search_products(
    main_query: AsyncSearch = Depends(build_search_query),
    es_client: PydanticESClient = Depends(get_es_client),
) -> ProductsListResponse:
    """
    Поиск товаров с использованием AsyncSearch DSL

    Args:
        main_query: объект AsyncSearch
        es_client: Клиент PydanticESClient

    Returns:
        ProductsListResponse со списком товаров и метаданными
    """
    try:
        search = main_query.using(es_client).index([f"{settings.ES_PRODUCTS_BASE_ALIAS}{WRITE_SUFFIX}"])
        response = await search.execute()
        products = [ProductResponse.model_validate(hit.to_dict()) for hit in response]
        return ProductsListResponse(products=products)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error searching products: {str(e)}")


# ============ READ (aggregations - brands) ============
@router.get(
    "/brands/all",
    response_model=BrandsResponse,
    summary="Получить все бренды",
    description="Получение списка всех уникальных брендов товаров",
)
async def get_all_brands(
    es_client: PydanticESClient = Depends(get_pydantic_es_client),
) -> BrandsResponse:
    """
    Получение списка всех брендов

    Args:
        es_client: Клиент Elasticsearch

    Returns:
        BrandsResponse со списком брендов
    """
    try:
        # Создаем запрос с агрегацией по брендам
        search_query = AsyncSearch()
        search_query.aggs.bucket("unique_brands", Terms(field="brand", size=1000))

        result = await es_client.aggregate(body=search_query.to_dict())

        # Извлекаем бренды из агрегации и преобразуем в enum
        buckets = result["aggregations"]["unique_brands"]["buckets"]
        brands = []
        for bucket in buckets:
            brand_value = bucket["key"]
            brand_enum = Brand(brand_value)
            brands.append(brand_enum)

        return BrandsResponse(
            brands=brands,
            total=len(brands),
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error getting brands: {str(e)}",
        )


# ============ UPDATE (full за исключением id, created_date и тд) ============
@router.put(
    "/{product_id}",
    summary="Полностью обновить товар",
    description="Полное обновление всех полей товара",
)
async def update_product(
    request: Request,
    product_id: str,
    product_data: ProductUpdateInput,
):
    """
    Полное обновление товара

    Args:
        request:
        product_id: ID товара для обновления
        product_data: Новые данные товара

    Returns:
        ProductUpdateResponse с сообщением об успехе

    Raises:
        HTTPException 404: если товар не найден
    """
    try:
        product_data = product_data.model_dump()
        product_data["id"] = product_id
        m = Message(method=ESMethod.UPDATE, kwargs=dict(document=product_data))
        await request.app.state.es_write_publisher.publish(m, exclude_unset=True)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error updating product: {str(e)}",
        )


# ============ UPDATE (partial) ============
@router.patch(
    "/{product_id}",
    response_model=ProductUpdateResponse,
    summary="Частично обновить товар",
    description="Частичное обновление только указанных полей товара",
)
async def partial_update_product(
    product_id: str,
    product_data: ProductUpdateInput,
    es_client: PydanticESClient = Depends(get_pydantic_es_client),
) -> ProductUpdateResponse:
    """
    Частичное обновление товара

    Args:
        product_id: ID товара для обновления
        product_data: Данные для обновления (только изменяемые поля)
        es_client: Клиент Elasticsearch

    Returns:
        ProductUpdateResponse с сообщением об успехе

    Raises:
        HTTPException 404: если товар не найден
    """
    try:
        # Фильтруем None значения TODO: попробовать updates = product_data.model_dump(exclude_none=True)
        updates = {k: v for k, v in product_data.model_dump().items() if v is not None}

        if not updates:
            return ProductUpdateResponse(message="No fields to update")

        # Выполняем частичное обновление
        await es_client.partial_update(
            doc_id=product_id,
            updates=updates,
        )

        return ProductUpdateResponse()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error partially updating product: {str(e)}",
        )


# ============ DELETE ============
@router.delete(
    "/{product_id}",
    response_model=ProductDeleteResponse,
    summary="Удалить товар",
    description="Удаление товара по ID",
)
async def delete_product(
    product_id: str,
    es_client: PydanticESClient = Depends(get_pydantic_es_client),
) -> ProductDeleteResponse:
    """
    Удаление товара

    Args:
        product_id: ID товара для удаления
        es_client: Клиент Elasticsearch

    Returns:
        ProductDeleteResponse с сообщением об успехе

    Raises:
        HTTPException 404: если товар не найден
    """
    try:
        # Удаляем товар
        # TODO: на самом деле, ничего не возвращается в этом методе...
        docs = await es_client.delete_by_id(doc_id=product_id)
        return ProductDeleteResponse(doc=docs)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Error deleting product: {str(e)}",
        )
