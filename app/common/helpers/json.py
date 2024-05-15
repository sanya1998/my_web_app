from json import JSONEncoder

from pydantic import BaseModel


class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set | tuple):
            return list(obj)
        if isinstance(obj, int | None):
            return obj
        if isinstance(obj, BaseModel):
            return {key: self.default(value) for key, value in obj.model_dump().items()}
        else:
            return super().default(obj)
