from typing import TypedDict

from fastapi import Request
from hawkcatcher.types import HawkCatcherSettings  # # User, Addons
from starlette.applications import Starlette


class FastapiAddons(TypedDict):
    url: str  # url of request
    method: str  # method of request
    headers: dict  # headers of request
    cookies: dict  # cookies of request
    params: dict  # request params


class Addons(TypedDict):
    """Additional data to be send with event due to frameworks"""

    pass


class Addons(Addons):
    fastapi: FastapiAddons


class FastapiSettings(HawkCatcherSettings[Request]):
    """Settings for Fastapi catcher for errors tracking"""

    app_instance: Starlette  # Fastapi app instance to add catching
