"""
Документ для товаров в Elasticsearch.
"""

from app.config.common import settings
from elasticsearch.dsl import AsyncDocument, Boolean, Date, Float, HalfFloat, InnerDoc, Integer, Keyword, Nested, Object
from es.dsl.analysis import RUSSIAN_ANALYSIS_SETTINGS
from es.dsl.fields import RussianKeywordField, RussianTextField, RussianTextWithKeywordField


class VariantDocument(InnerDoc):
    """Вложенный документ для вариантов товара (цвет, размер и т.д.)."""

    color = RussianKeywordField()  # Цвет с нормализацией
    size = Keyword()  # Размер (ключевое поле без нормализации)
    price_modifier = Float()  # Модификатор цены для варианта
    stock = Integer()  # Остаток на складе
    sku = Keyword()  # Артикул (SKU)


class ProductDocument(AsyncDocument):
    """Документ товара для полнотекстового поиска и фильтрации."""

    # Текстовое поле с русским анализом и дополнительным точным поиском
    product_name = RussianTextWithKeywordField()
    # Аналогично:
    # product_name = Text(
    #     analyzer="russian_index",           # Для индексации
    #     search_analyzer="russian_search",   # Для поиска
    #     fields={
    #         "exact": Keyword(normalizer="lowercase_normalizer")  # Чтобы текст использовать для точного поиска
    #     }
    # )

    # Ключевые поля с нормализацией для case-insensitive фильтрации
    category = RussianKeywordField()  # Категория товара
    # Аналогично:
    # category = Keyword(normalizer="lowercase_normalizer")
    brand = RussianKeywordField()  # Бренд

    # Числовые поля
    base_price = Float()  # Базовая цена (точность float)
    rating = HalfFloat()  # Рейтинг (половинная точность, экономит место)

    # Текстовое описание с русским анализом
    description = RussianTextField()  # Полное описание товара
    # Аналогично:
    # description = Text(
    #     analyzer="russian_index",
    #     search_analyzer="russian_search"
    # )

    # Ключевые поля для фильтрации
    features = RussianKeywordField()  # Характеристики товара
    tags = RussianKeywordField()  # Теги для категоризации

    # Булевы поля
    is_available = Boolean()  # Доступен для покупки
    is_on_sale = Boolean()  # Участвует в распродаже

    # Дата создания
    created_date = Date()  # Дата добавления товара в каталог

    # Объект с динамическими спецификациями
    specifications = Object(enabled=True)
    """
    Динамические спецификации товара.
    Пример: {"screen": "6.1", "camera": "12MP"}
    Тип object позволяет простые запросы вида:
    specifications.screen: "6.1"
    """

    # Вложенные варианты товара
    variants = Nested(VariantDocument)
    """
    Варианты товара (цвет/размер).
    Тип nested позволяет сложные фильтры:
    - variants.color: "красный" AND variants.size: "XL"
    - Агрегации по вариантам с учётом вложенности
    """

    class Index:
        """Настройки индекса товаров."""

        name = f"{settings.ES_PRODUCTS_BASE_ALIAS}_v2"

        settings = {
            "number_of_shards": 3,  # Количество шардов
            "number_of_replicas": 0,  # Количество реплик (0 для тестов)
            "analysis": RUSSIAN_ANALYSIS_SETTINGS,
        }
