# TODO: удалить весь файл и связи с ним после того, как будет проведена работа с графаной
import time
from random import random
from typing import Annotated

from app.dependencies.auth import AdminUserDep
from fastapi import APIRouter, Body
from pydantic import BaseModel

router = APIRouter(prefix="/testing")


@router.get(path="/long")
def long_answer(admin: AdminUserDep) -> float:
    waiting = random() * 5
    time.sleep(waiting)
    return waiting


@router.get(path="/error")
def get_error(admin: AdminUserDep, d: int = 0):
    if random() > 0.5:
        raise ZeroDivisionError
    else:
        raise KeyError


@router.get(path="/memory")
def memory(admin: AdminUserDep):
    _ = [i for i in range(10_000_000)]
    return 0


class Item(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float | None = 10.5
    tags: list[str] | None = []


@router.patch("/items/{item_id}", response_model=None)
async def update_item(item_id: str, item: Annotated[Item, Body()]):
    update_data = item.model_dump(exclude_unset=True)
    return update_data
