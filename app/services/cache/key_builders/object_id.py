delimiter = ":"
mark_one = "O"


def build_key_by_object_id(*args, **kwargs) -> str:
    key = f"{delimiter}".join([mark_one, repr(kwargs.get("object_id"))])
    return key
