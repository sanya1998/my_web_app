from pydantic import BaseModel


class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        use_enum_values = True
