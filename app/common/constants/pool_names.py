from enum import Enum


class PoolNameEnum(str, Enum):
    NullPool = "NullPool"
    StaticPool = "StaticPool"
    QueuePool = "QueuePool"
    AsyncAdaptedQueuePool = "AsyncAdaptedQueuePool"
    SingletonThreadPool = "SingletonThreadPool"
