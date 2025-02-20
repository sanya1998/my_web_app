from enum import Enum


class Environments(str, Enum):
    BASE = "base"
    TEST = "test"
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"
