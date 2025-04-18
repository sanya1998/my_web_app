# TODO: удалить весь файл и связи с ним
import time
from random import random

from fastapi import APIRouter

router = APIRouter(prefix="/testing")


@router.get(path="/long")
def long_answer() -> float:
    waiting = random() * 5
    time.sleep(waiting)
    return waiting


@router.get(path="/error")
def get_error():
    if random() > 0.5:
        raise ZeroDivisionError
    else:
        raise KeyError


@router.get(path="/memory")
def memory():
    _ = [i for i in range(10_000_000)]
    return 0
