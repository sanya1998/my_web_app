import asyncio
import random
from enum import Enum
from typing import Any, Dict, List

from app.config.common import settings
from es.clients.base import BaseESClient
from es.data_models.products import ProductCreateIn, VariantIn
from faker import Faker

fake = Faker()


class Category(str, Enum):
    SMARTPHONE = "smartphone"
    LAPTOP = "laptop"
    TABLET = "tablet"
    HEADPHONES = "headphones"
    SMARTWATCH = "smartwatch"
    CAMERA = "camera"


class SpecKey(str, Enum):
    SCREEN = "screen"
    STORAGE = "storage"
    RAM = "ram"
    BATTERY = "battery"
    TYPE = "type"
    RESOLUTION = "resolution"
    MEGAPIXELS = "megapixels"


class Feature(str, Enum):
    WIRELESS = "Wireless"
    WATER_RESISTANT = "Water Resistant"
    NOISE_CANCELLING = "Noise Cancelling"
    VOICE_ASSISTANT = "Voice Assistant"
    FACE_ID = "Face ID"
    FINGERPRINT = "Fingerprint Reader"
    TOUCHSCREEN = "Touchscreen"
    BACKLIT_KEYBOARD = "Backlit Keyboard"
    GPS = "GPS"
    HEART_RATE = "Heart Rate Monitor"
    SLEEP_TRACKING = "Sleep Tracking"
    STYLUS_SUPPORT = "Stylus Support"
    KEYBOARD_CASE = "Keyboard Case"
    WIRELESS_CHARGING = "Wireless Charging"
    FIVE_G = "5G"
    FOUR_G_LTE = "4G LTE"
    THUNDERBOLT = "Thunderbolt"
    IMAGE_STABILIZATION = "Image Stabilization"
    FOUR_K_VIDEO = "4K Video"
    FOLDABLE = "Foldable"


BRANDS = {
    Category.SMARTPHONE: ["Apple", "Samsung", "Google", "Xiaomi"],
    Category.LAPTOP: ["Apple", "Dell", "Lenovo", "HP"],
    Category.TABLET: ["Apple", "Samsung", "Microsoft"],
    Category.HEADPHONES: ["Sony", "Bose", "Apple", "JBL"],
    Category.SMARTWATCH: ["Apple", "Samsung", "Garmin"],
    Category.CAMERA: ["Canon", "Nikon", "Sony"],
}

PRICE_RANGES = {
    Category.SMARTPHONE: (300, 1500),
    Category.LAPTOP: (500, 3000),
    Category.TABLET: (200, 1200),
    Category.HEADPHONES: (50, 500),
    Category.SMARTWATCH: (150, 800),
    Category.CAMERA: (400, 2500),
}

SPECIFICATIONS = {
    Category.SMARTPHONE: {
        SpecKey.SCREEN: [6.1, 6.5, 6.7],
        SpecKey.STORAGE: [64, 128, 256],
        SpecKey.RAM: [4, 6, 8],
        SpecKey.BATTERY: [3000, 4000, 5000],
    },
    Category.LAPTOP: {
        SpecKey.SCREEN: [13, 14, 15, 16],
        SpecKey.STORAGE: [256, 512, 1024],
        SpecKey.RAM: [8, 16],
        SpecKey.RESOLUTION: ["FHD", "QHD", "4K"],
    },
    Category.HEADPHONES: {
        SpecKey.TYPE: ["Over-ear", "In-ear", "On-ear"],
        SpecKey.BATTERY: range(10, 31),
    },
    Category.CAMERA: {
        SpecKey.MEGAPIXELS: [24, 36, 45, 61],
        SpecKey.RESOLUTION: ["20MP", "24MP", "30MP", "45MP"],
    },
    Category.SMARTWATCH: {
        SpecKey.SCREEN: [1.2, 1.4, 1.6, 1.8],
        SpecKey.BATTERY: range(1, 8),
    },
    Category.TABLET: {
        SpecKey.SCREEN: [10, 11, 12, 13],
        SpecKey.STORAGE: [64, 128, 256],
        SpecKey.RAM: [4, 6, 8],
    },
}

FEATURES = {
    Category.SMARTPHONE: [
        Feature.FIVE_G,
        Feature.FACE_ID,
        Feature.WIRELESS_CHARGING,
        Feature.WATER_RESISTANT,
    ],
    Category.LAPTOP: [
        Feature.BACKLIT_KEYBOARD,
        Feature.TOUCHSCREEN,
        Feature.THUNDERBOLT,
        Feature.FINGERPRINT,
    ],
    Category.HEADPHONES: [
        Feature.NOISE_CANCELLING,
        Feature.WIRELESS,
        Feature.VOICE_ASSISTANT,
        Feature.FOLDABLE,
    ],
    Category.CAMERA: [
        Feature.FOUR_K_VIDEO,
        Feature.IMAGE_STABILIZATION,
        Feature.WIRELESS,
        Feature.TOUCHSCREEN,
    ],
    Category.SMARTWATCH: [
        Feature.HEART_RATE,
        Feature.GPS,
        Feature.WATER_RESISTANT,
        Feature.SLEEP_TRACKING,
    ],
    Category.TABLET: [
        Feature.STYLUS_SUPPORT,
        Feature.KEYBOARD_CASE,
        Feature.FACE_ID,
        Feature.FOUR_G_LTE,
    ],
}

COLORS = ["Black", "White", "Silver", "Blue", "Red", "Space Gray", "Midnight Green"]


def format_spec_value(spec_key: SpecKey, value: Any) -> str:
    """Форматирование значения спецификации"""
    match spec_key:
        case SpecKey.SCREEN:
            return f'{value}"'
        case SpecKey.STORAGE | SpecKey.RAM:
            return f"{value}GB"
        case SpecKey.BATTERY:
            return f"{value}h" if value > 10 else f"{value} days"
        case SpecKey.MEGAPIXELS:
            return f"{value}MP"
        case _:
            return str(value)


def generate_specifications(category: Category) -> Dict[str, Any]:
    """Генерация спецификаций на основе конфигурации"""
    if category not in SPECIFICATIONS:
        return {}

    specs_config = SPECIFICATIONS[category]
    specs = {}

    for spec_key, values in specs_config.items():
        value = random.choice(values)
        specs[spec_key.value] = format_spec_value(spec_key, value)

    return specs


def generate_features(category: Category) -> List[str]:
    """Генерация фич на основе конфигурации"""
    category_features = FEATURES.get(category, [])
    selected_features = random.sample(category_features, k=min(3, len(category_features)))
    return [feature.value for feature in selected_features]


def generate_search_content(
    product_name: str,
    category: Category,
    brand: str,
    description: str,
    features: List[str],
) -> str:
    """Генерация поля для поиска - конкатенация важных данных"""
    features_text = " ".join(features)
    return f"{product_name} {category.value} {brand} {description} {features_text}"


def generate_variants(base_price: float) -> List[VariantIn]:
    """Генерация вариантов товара"""
    variants = []
    colors = random.sample(COLORS, k=random.randint(1, 3))

    for i, color in enumerate(colors):
        variant = VariantIn(
            color=color,
            size=random.choice(["standard", "large", "XL"]),
            price_modifier=round(random.uniform(-50, 100), 2),  # Скидка или надбавка
            stock=random.randint(0, 50),
            sku=f"{color[:3].upper()}{random.randint(100, 999)}",  # Генерация SKU
        )
        variants.append(variant)

    return variants


def generate_product(_id: str) -> ProductCreateIn:
    """Генерация одного товара для записи"""
    category = random.choice(list(Category))
    brand = random.choice(BRANDS[category])

    min_price, max_price = PRICE_RANGES[category]
    base_price = round(random.uniform(min_price, max_price), 2)

    discount = random.choice([0, 0, 0, 10, 20])
    if discount > 0:
        base_price = base_price * (1 - discount / 100)
        base_price = round(base_price, 2)

    features_list = generate_features(category)
    description = fake.sentence(nb_words=12) + fake.paragraph(nb_sentences=6)
    product_name_text = f"{brand} {fake.word().title()} {random.randint(1, 15)}"

    # Генерируем варианты
    variants = generate_variants(base_price)

    # Вычисляем is_available на основе вариантов
    is_available = any(v.stock > 0 for v in variants)

    search_content = generate_search_content(
        product_name=product_name_text,
        category=category,
        brand=brand,
        description=description,
        features=features_list,
    )

    return ProductCreateIn(
        id=_id,
        product_name=product_name_text,
        category=category,
        brand=brand,
        base_price=base_price,
        rating=round(random.uniform(3.0, 5.0), 1),
        description=description,
        search_content=search_content,
        specifications=generate_specifications(category),
        features=features_list,
        is_available=is_available,
        is_on_sale=discount > 0,
        created_date=fake.date_this_year(),
        tags=[category.value, brand, fake.word(), fake.word()],
        variants=variants,
    )


async def generate_and_index_documents(es: BaseESClient, count=100000):
    """Генерация и индексация документов"""
    print(f"🚀 Генерация {count} документов...")

    batch = []

    for i in range(count):
        product = generate_product(_id=str(i))
        batch.append(product.model_dump())  # ProductIn -> dict

        if len(batch) >= 200:
            await es.bulk_create(documents=batch)
            batch = []
            print(f"📦 Индексировано {i + 1}/{count}")

    if batch:
        await es.bulk(body=batch)

    print(f"✅ Успешно индексировано {count} документов")


async def main():
    """Основная асинхронная функция"""
    async with BaseESClient(settings.ES_HOSTS, default_alias=settings.ES_PRODUCTS_BASE_ALIAS) as es:
        es: BaseESClient
        await generate_and_index_documents(es)

        await es.refresh_index(base_alias=settings.ES_PRODUCTS_BASE_ALIAS)
        result = await es.count(base_alias=settings.ES_PRODUCTS_BASE_ALIAS)
        print(f"📊 Всего документов в индексе: {result}")


if __name__ == "__main__":
    asyncio.run(main())
