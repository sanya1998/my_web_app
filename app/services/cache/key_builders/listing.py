from pydantic import BaseModel

delimiter = ":"
mark_many = "M"


#  TODO: filters мб прописать в скобках прям ?
#  TODO: проверить после того, как заработают новые фильтры
#  TODO: rename parameters
def build_key_by_listing(*args, **kwargs) -> str:
    parameters: BaseModel = kwargs.get("filters")
    filters = parameters.model_dump_json(exclude_none=True) if parameters else "{}"
    key = f"{delimiter}".join([mark_many, filters])
    return key


def build_key_pattern_by_listing(*args, **kwargs) -> str:
    key = f"{mark_many}{delimiter}*"
    return key
