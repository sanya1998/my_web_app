from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)  # TODO: check populate_by_name=True
