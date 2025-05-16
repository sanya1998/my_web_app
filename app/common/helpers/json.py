from datetime import date, datetime
from json import JSONEncoder

from pydantic import BaseModel


# TODO: написать тесты для енкодера
class CustomEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (set, tuple)):
            return list(obj)
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, BaseModel):
            return {key: self.default(value) for key, value in obj.model_dump(mode="json").items()}
        return super().default(obj)
