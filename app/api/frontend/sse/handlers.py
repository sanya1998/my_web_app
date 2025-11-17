import asyncio
import logging
from datetime import datetime

from app.common.constants.paths import SSE_PATH
from app.common.helpers.api_version import VersionedAPIRouter
from app.config.common import settings
from app.consumers.sse import SSEMessageSchema
from fastapi import Request
from sse_starlette.sse import EventSourceResponse

logger = logging.getLogger(__name__)
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
    sse_pubsub = request.app.state.sse_pubsub
    return EventSourceResponse(
        content=sse_pubsub.messages_listener(request),
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        ping=settings.SSE_PING_TIMEOUT,
    )


@router.post("/send_message")
async def send_sse_message_endpoint(request: Request, message_request: SSEMessageSchema):
    """Эндпоинт для отправки тестовых сообщений в SSE"""
    publisher_of_new_sse_messages = request.app.state.publisher_of_new_sse_messages
    await publisher_of_new_sse_messages.publish(message_request)
    return {"success": True}
