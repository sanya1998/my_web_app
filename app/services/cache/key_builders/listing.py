delimiter = ":"
mark_many = "M"


def build_key_by_listing(*args, filters, **kwargs) -> str:
    key = f"{delimiter}".join([mark_many, filters.model_dump_json(exclude_none=True)])
    return key


def build_key_pattern_by_listing(*args, **kwargs) -> str:
    key = f"{mark_many}{delimiter}*"
    return key
