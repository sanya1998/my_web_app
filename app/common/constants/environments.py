from enum import Enum


class Environments(str, Enum):
    TEST = "test"
    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"
