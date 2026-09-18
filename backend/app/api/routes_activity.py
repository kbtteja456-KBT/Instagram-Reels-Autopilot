"""Live Server-Sent Events (SSE) stream for real-time pipeline telemetry."""

import asyncio
import json
from typing import Set
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from backend.app.models.activity import ActivityLog
from backend.app.core.logging import logger

router = APIRouter(prefix="/activity", tags=["activity"])

# Active SSE client subscriber queues
_subscribers: Set[asyncio.Queue] = set()


async def broadcast_activity(item: ActivityLog) -> None:
    """Broadcast an activity event to all active SSE browser connections."""
    dead = []
    data_str = json.dumps(item.model_dump(), default=str)
    for q in list(_subscribers):
        try:
            q.put_nowait(data_str)
        except Exception:
            dead.append(q)
    for q in dead:
        _subscribers.discard(q)


@router.get("/stream")
async def activity_stream(request: Request):
    """Server-Sent Events endpoint streaming pipeline events to the frontend."""
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)
    _subscribers.add(queue)
    logger.info(f"[SSE] Browser client connected to activity stream (Total: {len(_subscribers)})")

    async def event_generator():
        try:
            # Send initial ping event
            init_item = ActivityLog(
                event_id="init",
                stage="SYSTEM",
                message="Connected to AI Instagram Reels Autopilot telemetry stream",
                level="SUCCESS"
            )
            yield f"data: {json.dumps(init_item.model_dump(), default=str)}\n\n"

            while True:
                # Check for client disconnect
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    # Keepalive heartbeat comment
                    yield ": ping\n\n"
        finally:
            _subscribers.discard(queue)
            logger.info("[SSE] Browser client disconnected from activity stream")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
