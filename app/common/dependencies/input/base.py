from pydantic import BaseModel


class BaseInput(BaseModel):
    pass
    # TODO in fastapi 0.114.0: model_config = {"extra": "forbid"}
