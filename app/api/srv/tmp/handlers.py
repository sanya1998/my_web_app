# TODO: удалить весь файл и связи с ним после того, как будет проведена работа с графаной
import time
from random import random
from typing import Annotated, List, Optional

from app.dependencies.auth.admin import AdminUserDep
from fastapi import APIRouter, Body, Depends, Query
from pydantic import BaseModel

router = APIRouter(prefix="/testing", dependencies=[AdminUserDep])


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


# Define a nested schema using Pydantic
class SubItem(BaseModel):
    name: str
    count: int


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    subitems: List[SubItem]


# Dependency function to handle complex query parameters
def get_item_query(
    name: str = Query(..., min_length=1), description: Optional[str] = Query(None), subitems: List[str] = Query(None)
) -> Item:
    # This simulates parsing 'subitems' which is a list of strings like 'name,count'
    subitems_parsed = []
    if subitems:
        for subitem in subitems:
            name, count = subitem.split(",")
            subitems_parsed.append(SubItem(name=name, count=int(count)))
    return Item(name=name, description=description, subitems=subitems_parsed)


@router.get("/items/")
async def read_items(item: Item = Depends(get_item_query)):
    return item
