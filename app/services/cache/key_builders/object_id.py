delimiter = ":"
mark_one = "O"


def build_key_by_object_id(*args, object_id, **kwargs) -> str:
    key = f"{delimiter}".join([mark_one, repr(object_id)])
    return key
