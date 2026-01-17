"""
Бенчмарк API v1 vs v2
Запуск: python benchmark_products_api.py
"""

import asyncio
import random
import statistics
import time

import aiohttp
from app.config.common import settings

TEST_PARAMS = {
    "page": 1,
    "per_page": 10,
    "sort_field": "created_date",
    "order": "desc",
    "categories": ["smartphone", "laptop", "tablet", "headphones", "smartwatch", "camera"],
    "brands": ["Apple", "Samsung", "Google", "Xiaomi", "Dell", "Lenovo", "HP", "Microsoft"],
    "features": ["Wireless", "Water Resistant", "Touchscreen", "GPS"],
    "colors": ["Black", "White", "Blue", "Red"],
    "min_price": 100,
    "max_price": 1000,
    "tags": ["new", "popular"],
    "search_query": ["", "phone", "smart"],
}


def build_params():
    """Случайные параметры с cache bust."""
    params = {
        "page": "1",
        "per_page": "10",
        "sort_field": "created_date",
        "order": "desc",
        "cache_bust": str(random.randint(1, 1_000_000)),
    }

    # Добавляем случайные фильтры
    if random.random() > 0.3:
        params["categories"] = random.choice(TEST_PARAMS["categories"])
    if random.random() > 0.3:
        params["brands"] = random.choice(TEST_PARAMS["brands"])
    if random.random() > 0.5:
        params["features"] = random.choice(TEST_PARAMS["features"])

    return params


async def benchmark_endpoint(session, url, name, n=20):
    """Запустить бенчмарк для одного эндпоинта."""
    print(f"\n📊 {name}: {url}")

    times = []
    for i in range(n):
        params = build_params()

        start = time.perf_counter()
        async with session.get(url, params=params, timeout=10) as r:
            elapsed = time.perf_counter() - start

            if r.status == 200:
                times.append(elapsed)
                print(f"  {i+1:2d}/{n}: {elapsed:.3f}s")
            else:
                print(f"  {i+1:2d}/{n}: ERROR {r.status}")

        await asyncio.sleep(0.1)

    if times:
        print(f"\n  Среднее: {statistics.mean(times):.3f}s")
        print(f"  Медиана: {statistics.median(times):.3f}s")
        print(f"  Min/Max: {min(times):.3f}s / {max(times):.3f}s")

    return times


async def main():
    """Основная функция."""
    base_url = f"http://{settings.API_HOST}:{settings.API_PORT}"

    print("🔬 Бенчмарк: v1 (PydanticESClient) vs v2 (AsyncSearch DSL)")
    print("=" * 50)

    async with aiohttp.ClientSession() as session:
        # Тест v1
        v1_times = await benchmark_endpoint(session, f"{base_url}/api/v1/products/", "v1")

        # Тест v2
        v2_times = await benchmark_endpoint(session, f"{base_url}/api/v2/products/", "v2")

        # Сравнение
        if v1_times and v2_times:
            print("\n" + "=" * 50)
            print("🏆 РЕЗУЛЬТАТЫ:")
            print("=" * 50)

            v1_avg = statistics.mean(v1_times)
            v2_avg = statistics.mean(v2_times)

            print(f"\nv1: {v1_avg:.3f}s (медиана: {statistics.median(v1_times):.3f}s)")
            print(f"v2: {v2_avg:.3f}s (медиана: {statistics.median(v2_times):.3f}s)")

            diff = v1_avg - v2_avg
            percent = (diff / v1_avg) * 100 if v1_avg > 0 else 0

            if diff > 0:
                print(f"\n📈 v2 быстрее на {abs(percent):.1f}% ({abs(diff):.3f}s)")
                print("✅ Рекомендация: использовать v2")
            elif diff < 0:
                print(f"\n📈 v1 быстрее на {abs(percent):.1f}% ({abs(diff):.3f}s)")
                print("⚠️  Рекомендация: оставить v1")
            else:
                print("\n⚖️  Производительность одинаковая")


if __name__ == "__main__":
    asyncio.run(main())
