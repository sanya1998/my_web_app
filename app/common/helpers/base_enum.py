from enum import Enum


# TODO: не используется, но, возможно, пригодится
class BaseEnum(str, Enum):
    @classmethod
    def contains(cls, item) -> bool:
        return item in cls._value2member_map_

    # TODO: проверить
    @classmethod
    def list(cls):
        """
        class OperationType(BaseEnum):
            CREATE = 'CREATE'
            DELETE = 'DELETE'

        logger.info(OperationType.list())
        > ['CREATE', 'DELETE']
        """
        return list(map(lambda c: c.value, cls))
