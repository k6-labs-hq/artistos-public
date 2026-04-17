from __future__ import annotations

import asyncio
import json
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone

from fastapi import WebSocket


@dataclass(slots=True)
class BufferedEvent:
    id: int
    event_type: str
    payload: dict
    created_at: str


class LiveUpdatesManager:
    def __init__(self, buffer_size: int = 500) -> None:
        self._connections: set[WebSocket] = set()
        self._lock = asyncio.Lock()
        self._buffer: deque[BufferedEvent] = deque(maxlen=buffer_size)
        self._next_event_id = 1

    async def connect(self, websocket: WebSocket, *, after_event_id: int | None = None) -> int:
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
            replay_events = self._events_after(after_event_id) if after_event_id else []

        for event in replay_events:
            await websocket.send_text(self._serialize_event(event))
        return len(replay_events)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections.discard(websocket)

    def _events_after(self, after_event_id: int) -> list[BufferedEvent]:
        return [event for event in self._buffer if event.id > after_event_id]

    def _serialize_event(self, event: BufferedEvent) -> str:
        return json.dumps(
            {
                "event_id": event.id,
                "event_type": event.event_type,
                "created_at": event.created_at,
                "payload": event.payload,
            },
            default=str,
        )

    async def broadcast(self, event_type: str, payload: dict) -> None:
        async with self._lock:
            event = BufferedEvent(
                id=self._next_event_id,
                event_type=event_type,
                payload=payload,
                created_at=datetime.now(timezone.utc).isoformat(),
            )
            self._next_event_id += 1
            self._buffer.append(event)
            connections = list(self._connections)

        message = self._serialize_event(event)
        stale: list[WebSocket] = []
        for connection in connections:
            try:
                await connection.send_text(message)
            except Exception:
                stale.append(connection)
        if stale:
            async with self._lock:
                for connection in stale:
                    self._connections.discard(connection)


live_updates_manager = LiveUpdatesManager()


def broadcast_live_update(event_type: str, payload: dict) -> None:
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    loop.create_task(live_updates_manager.broadcast(event_type, payload))