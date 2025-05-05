from pydantic import BaseModel, ConfigDict


class BaseInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
