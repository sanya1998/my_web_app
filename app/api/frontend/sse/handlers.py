import asyncio
from datetime import datetime

from app.common.constants.paths import SSE_PATH
from app.common.helpers.api_version import VersionedAPIRouter
from fastapi import Request
from sse_starlette.sse import EventSourceResponse

router = VersionedAPIRouter(prefix=SSE_PATH)


# sse server
@router.get("/datetime")
async def datetime_sse(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            yield datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())


# sse server
@router.get("/messages")
async def messages_sse(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break

            yield "новое сообщение"
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator())
