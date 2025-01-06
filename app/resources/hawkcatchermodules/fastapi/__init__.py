from .fastapi import HawkFastapi
from .types import FastapiSettings, HawkCatcherSettings

hawk = HawkFastapi()


def init(*args, **kwargs):
    hawk.init(*args, **kwargs)


def send(*args, **kwargs):
    hawk.send(*args, **kwargs)
