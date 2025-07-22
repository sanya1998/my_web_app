import time

import httpx


def scale_one(_url: str):
    start_time = time.perf_counter()
    httpx.get(_url)
    process_time = time.perf_counter() - start_time
    print(f"\tSeconds:\t{process_time}")
    return process_time


def scale_all(attempts: int, _url: str):
    results = []
    summ = 0.0
    for i in range(attempts):
        seconds = scale_one(_url=_url)
        results.append(seconds)
        summ += seconds
    average = summ / attempts
    print(f"Average seconds: {average}\n")


if __name__ == "__main__":
    url = "http://0.0.0.0:8000/api/v1/hotels/"
    scale_one(url)  # Чтобы записалось в кеш
    scale_all(attempts=10, _url=url)
    # Average seconds: 0.014312070698360912
    # Average seconds: 0.012933908400009386 protocol=-1
    # Average seconds: 0.010695733298780397 no logger
