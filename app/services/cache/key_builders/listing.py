from pydantic import BaseModel

delimiter = ":"
mark_many = "M"


#  TODO: filters мб прописать в скобках прям ?
def build_key_by_listing(*args, **kwargs) -> str:
    filters_pydantic: BaseModel = kwargs.get("filters")
    filters = filters_pydantic.model_dump_json(exclude_none=True) if filters_pydantic else "{}"
    key = f"{delimiter}".join([mark_many, filters])
    return key


def build_key_pattern_by_listing(*args, **kwargs) -> str:
    key = f"{mark_many}{delimiter}*"
    return key
