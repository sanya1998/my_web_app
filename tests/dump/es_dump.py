# Детерминированная генерация данных
from datetime import date
from typing import Any, Dict, List

from app.config.common import settings
from es.clients.pydantic_ import PydanticESClient
from es.schemas.products import (
    BRANDS_MAP,
    FEATURES,
    PRICE_RANGES,
    SPECIFICATIONS,
    Category,
    Color,
    Feature,
    ProductCreateSchema,
    Size,
    SpecKey,
    VariantIn,
    format_spec_value,
)
from faker import Faker


def get_fake_for_doc(doc_number: int) -> Faker:
    """
    Возвращает детерминированный Faker для конкретного документа

    Каждый документ получает свой уникальный seed на основе базового seed=0
    Это гарантирует что:
    1. Все данные детерминированы (одинаковые при каждом запуске)
    2. Каждый документ уникален
    3. Данные реалистичны и разнообразны
    """
    fake = Faker()
    fake.seed_instance(seed=doc_number)  # seed = doc_number для уникальности
    return fake


def deterministic_choice(seq: List[Any], doc_number: int) -> Any:
    """Детерминированный выбор элемента из списка"""
    return seq[doc_number % len(seq)]


def deterministic_sample(seq: List[Any], k: int, doc_number: int) -> List[Any]:
    """Детерминированная выборка k элементов"""
    step = (doc_number % 7) + 1  # 1-7
    indices = [(doc_number + i * step) % len(seq) for i in range(k)]
    return [seq[i] for i in indices if i < len(seq)]


def deterministic_float(min_val: float, max_val: float, doc_number: int) -> float:
    """Детерминированное float значение"""
    normalized = (doc_number % 10000) / 10000.0
    return min_val + normalized * (max_val - min_val)


def deterministic_int(min_val: int, max_val: int, doc_number: int) -> int:
    """Детерминированное int значение"""
    return min_val + (doc_number % (max_val - min_val + 1))


def generate_specifications(category: Category, doc_number: int) -> Dict[SpecKey, Any]:
    """Детерминированная генерация спецификаций"""
    specs_config = SPECIFICATIONS[category]
    specs = {}

    for spec_key, values in specs_config.items():
        value = deterministic_choice(values, doc_number)
        specs[spec_key] = format_spec_value(spec_key, value)

    return specs


def generate_features(category: Category, doc_number: int) -> List[Feature]:
    """Детерминированная генерация фич"""
    category_features = FEATURES[category]
    num_features = 1 + (doc_number % 3)

    return deterministic_sample(list(category_features), num_features, doc_number)


def generate_variants(doc_number: int) -> List[VariantIn]:
    """Детерминированная генерация вариантов"""
    variants = []
    num_variants = doc_number % 3

    for i in range(num_variants):
        variant_seed = doc_number * 100 + i

        variant = VariantIn(
            color=deterministic_choice(list(Color), variant_seed),
            size=deterministic_choice(list(Size), variant_seed),
            price_modifier=deterministic_float(-50, 100, variant_seed),
            stock=deterministic_int(0, 50, variant_seed),
            sku=f"SKU{doc_number:04d}_{i:02d}",
        )
        variants.append(variant)

    return variants


def generate_product(doc_number: int) -> ProductCreateSchema:
    """Детерминированная генерация одного товара с Faker"""
    fake = get_fake_for_doc(doc_number)

    # Базовые данные (как были)
    categories = list(Category)
    category = deterministic_choice(categories, doc_number)
    brand = deterministic_choice(BRANDS_MAP[category], doc_number)

    min_price, max_price = PRICE_RANGES[category]
    base_price = deterministic_float(min_price, max_price, doc_number)
    base_price = round(base_price, 2)

    discount = 20 if doc_number % 5 == 0 else 0
    if discount > 0:
        base_price = round(base_price * (1 - discount / 100), 2)

    features_list = generate_features(category, doc_number)

    # УЛУЧШЕНИЕ С FAKER: более натуральные названия и описания
    product_name_text = f"{brand.value} {fake.catch_phrase()}"
    description = fake.paragraph(nb_sentences=3)

    variants = generate_variants(doc_number)
    is_available = len(variants) > 0 and any(v.stock > 0 for v in variants)

    # УЛУЧШЕНИЕ С FAKER: реалистичные даты в диапазоне
    start_date = date(2024, 1, 1)
    created_date = fake.date_between(start_date=start_date, end_date="+1y")

    # УЛУЧШЕНИЕ С FAKER: разнообразные теги
    base_tags = [category.value, brand.value.lower(), "electronics"]
    fake_tags = fake.words(nb=3)  # 3 случайных слова
    tag_options = base_tags + fake_tags

    num_tags = 1 + (doc_number % 3)
    tags = deterministic_sample(tag_options, num_tags, doc_number)

    return ProductCreateSchema(
        id=str(doc_number),
        product_name=product_name_text,
        category=category,
        brand=brand,
        base_price=base_price,
        rating=3.0 + (doc_number % 10) * 0.2,
        description=description,
        specifications=generate_specifications(category, doc_number),
        features=features_list,
        is_available=is_available,
        is_on_sale=discount > 0,
        created_date=created_date,
        tags=tags,
        variants=variants,
    )


def generate_test_products(count: int = 10) -> List[ProductCreateSchema]:
    """Генерация фиксированных тестовых данных"""
    return [generate_product(i) for i in range(count)]


async def generate_and_index_test_data(
    es: PydanticESClient,
    count: int = 100,
    batch_size: int = 25,
) -> None:
    """
    Детерминированная генерация тестовых данных с Faker
    """
    split_point = count // 2

    # Single индексация
    for i in range(split_point):
        await es.index(
            document=generate_product(i),
            base_alias=settings.ES_PRODUCTS_BASE_ALIAS,
        )

    # Bulk индексация батчами
    for i in range(split_point, count, batch_size):
        batch = [generate_product(j) for j in range(i, min(i + batch_size, count))]
        await es.bulk_index(documents=batch, base_alias=settings.ES_PRODUCTS_BASE_ALIAS)

    await es.refresh_index(base_alias=settings.ES_PRODUCTS_BASE_ALIAS)
    actual_count = await es.count(base_alias=settings.ES_PRODUCTS_BASE_ALIAS)
    print(f"✅ Индексация завершена. В индексе: {actual_count} документов")
