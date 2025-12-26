from dataclasses import dataclass
from typing import Optional


@dataclass
class AliasInfo:
    index: str
    alias: str


@dataclass
class AddAliasInfo(AliasInfo):
    is_write_index: Optional[bool] = False


@dataclass
class AddAlias:
    add: AddAliasInfo


@dataclass
class RemoveAlias:
    remove: AliasInfo
