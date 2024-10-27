from pydantic import BaseModel

delimiter = ":"
mark_many = "M"


def build_key_by_listing(*args, **kwargs) -> str:
    raw_filters: BaseModel = kwargs.get("raw_filters")
    # Есть pagination, который синонимичен limit и offset
    filters = raw_filters.model_dump_json(exclude_none=True, exclude={"limit", "offset"}) if raw_filters else "{}"
    key = f"{delimiter}".join([mark_many, filters])
    return key


def build_key_pattern_by_listing(*args, **kwargs) -> str:
    key = f"{mark_many}{delimiter}*"
    return key
