from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional

from app.common.schemas.base import BaseSchema
from pydantic import Field, computed_field


class Category(str, Enum):
    SMARTPHONE = "smartphone"
    LAPTOP = "laptop"
    TABLET = "tablet"
    HEADPHONES = "headphones"
    SMARTWATCH = "smartwatch"
    CAMERA = "camera"


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


class Brand(str, Enum):
    APPLE = "Apple"
    SAMSUNG = "Samsung"
    GOOGLE = "Google"
    XIAOMI = "Xiaomi"
    DELL = "Dell"
    LENOVO = "Lenovo"
    HP = "HP"
    MICROSOFT = "Microsoft"
    BOSE = "Bose"
    JBL = "JBL"
    GARMIN = "Garmin"
    CANON = "Canon"
    NIKON = "Nikon"
    SONY = "Sony"


class Color(str, Enum):
    BLACK = "Black"
    WHITE = "White"
    SILVER = "Silver"
    BLUE = "Blue"
    RED = "Red"
    SPACE_GRAY = "Space Gray"
    MIDNIGHT_GREEN = "Midnight Green"


class Size(str, Enum):
    STANDARD = "standard"
    LARGE = "large"
    XL = "XL"


class SpecKey(str, Enum):
    SCREEN = "screen"
    STORAGE = "storage"
    RAM = "ram"
    BATTERY = "battery"
    TYPE = "type"
    RESOLUTION = "resolution"
    MEGAPIXELS = "megapixels"


BRANDS_MAP = {
    Category.SMARTPHONE: [Brand.APPLE, Brand.SAMSUNG, Brand.GOOGLE, Brand.XIAOMI],
    Category.LAPTOP: [Brand.APPLE, Brand.DELL, Brand.LENOVO, Brand.HP],
    Category.TABLET: [Brand.APPLE, Brand.SAMSUNG, Brand.MICROSOFT],
    Category.HEADPHONES: [Brand.SONY, Brand.BOSE, Brand.APPLE, Brand.JBL],
    Category.SMARTWATCH: [Brand.APPLE, Brand.SAMSUNG, Brand.GARMIN],
    Category.CAMERA: [Brand.CANON, Brand.NIKON, Brand.SONY],
}


PRICE_RANGES = {
    Category.SMARTPHONE: (300, 1500),
    Category.LAPTOP: (500, 3000),
    Category.TABLET: (200, 1200),
    Category.HEADPHONES: (50, 500),
    Category.SMARTWATCH: (150, 800),
    Category.CAMERA: (400, 2500),
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
        SpecKey.RESOLUTION: ["HD", "FHD", "QHD", "4K"],
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


def format_spec_value(spec_key: SpecKey, value: Any) -> str:
    """Форматирование значения спецификации"""
    match spec_key:
        case SpecKey.SCREEN:
            return f'{value}"'
        case SpecKey.STORAGE | SpecKey.RAM:
            return f"{value}GB"
        case SpecKey.BATTERY:
            return f"{value}h"
        case SpecKey.MEGAPIXELS:
            return f"{value}MP"
        case _:
            return str(value)


class VariantIn(BaseSchema):
    """Вариант товара для записи (без вычисляемых полей)"""

    color: Color
    size: Size = Field(default=Size.STANDARD)
    price_modifier: float = Field(default=0.0)
    stock: int = Field(default=0)
    sku: Optional[str] = None


class ProductCreateSchema(BaseSchema):
    """Модель товара для записи в Elasticsearch"""

    id: str
    product_name: str
    category: Category
    brand: Brand
    base_price: float = Field(gt=0, description="Цена должна быть положительной")
    rating: float = Field(ge=0, le=5, description="Рейтинг от 0 до 5")
    description: str
    specifications: Dict[SpecKey, Any]
    features: List[Feature] = Field(default_factory=list)
    is_available: bool = True
    is_on_sale: bool = False
    created_date: date = Field(default_factory=date.today)
    tags: List[str] = Field(default_factory=list)
    variants: Optional[List[VariantIn]] = None


class ProductUpdateSchema(BaseSchema):
    """Модель товара для обновления в Elasticsearch"""

    id: str
    product_name: Optional[str] = None
    category: Optional[Category] = None
    brand: Optional[Brand] = None
    base_price: float = Field(gt=0, description="Цена должна быть положительной")
    rating: float = Field(ge=0, le=5, description="Рейтинг от 0 до 5")
    description: Optional[str] = None
    specifications: Optional[Dict[SpecKey, Any]] = None
    features: Optional[List[Feature]] = None
    is_available: Optional[bool] = None
    is_on_sale: Optional[bool] = None
    tags: Optional[List[str]] = None
    variants: Optional[List[VariantIn]] = None


class ProductReadSchema(ProductCreateSchema):
    """Модель товара для чтения из Elasticsearch (с вычисляемыми полями)"""

    @computed_field
    @property
    def total_stock(self) -> int:
        """Общий остаток по всем вариантам"""
        if not self.variants:
            return 0
        return sum(variant.stock for variant in self.variants)

    @computed_field
    @property
    def min_price(self) -> float:
        """Минимальная цена с учетом вариантов"""
        if not self.variants:
            return self.base_price

        min_price = self.base_price
        for variant in self.variants:
            variant_price = self.base_price + variant.price_modifier
            if variant_price < min_price:
                min_price = variant_price
        return min_price

    @computed_field
    @property
    def max_price(self) -> float:
        """Максимальная цена с учетом вариантов"""
        if not self.variants:
            return self.base_price

        max_price = self.base_price
        for variant in self.variants:
            variant_price = self.base_price + variant.price_modifier
            if variant_price > max_price:
                max_price = variant_price
        return max_price

    @computed_field
    @property
    def available_colors(self) -> List[Color]:
        """Доступные цвета (варианты с остатком > 0)"""
        if not self.variants:
            return []

        colors = []
        for variant in self.variants:
            if variant.stock > 0:
                colors.append(variant.color)
        return colors

    @computed_field
    @property
    def price_range(self) -> str:
        """Диапазон цен для отображения"""
        if self.min_price and self.max_price:
            if self.min_price == self.max_price:
                return f"${self.min_price:.2f}"
            return f"${self.min_price:.2f} - ${self.max_price:.2f}"
        return f"${self.base_price:.2f}"

    @computed_field
    @property
    def has_variants(self) -> bool:
        """Есть ли варианты у товара"""
        return bool(self.variants)


# TODO: сделать аккуратное наследование, чтобы минимизировать дублирование


class ProductShortReadSchema(BaseSchema):
    product_name: str
    brand: Brand
    base_price: float = Field(gt=0, description="Цена должна быть положительной")
    rating: float = Field(ge=0, le=5, description="Рейтинг от 0 до 5")
    variants: Optional[List[VariantIn]] = None
