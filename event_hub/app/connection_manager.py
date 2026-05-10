import asyncio
import logging
from typing import Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self, heartbeat_interval: int = 30) -> None:
        self._connections: dict[str, set[WebSocket]] = {}
        self._heartbeat_tasks: dict[WebSocket, asyncio.Task[None]] = {}
        self._heartbeat_interval = heartbeat_interval
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, topic: str) -> None:
        async with self._lock:
            self._connections.setdefault(topic, set()).add(websocket)
        self._heartbeat_tasks[websocket] = asyncio.create_task(
            self._heartbeat_loop(websocket)
        )
        logger.info(f"Client connected to topic '{topic}'")

    async def disconnect(self, websocket: WebSocket, topic: str) -> None:
        async with self._lock:
            self._connections.get(topic, set()).discard(websocket)
            if topic in self._connections and not self._connections[topic]:
                del self._connections[topic]
        self._cancel_heartbeat(websocket)
        logger.info(f"Client disconnected from topic '{topic}'")

    async def broadcast(self, topic: str, message: dict[str, Any]) -> None:
        async with self._lock:
            clients = self._connections.get(topic, set()).copy()

        disconnected = []
        for client in clients:
            try:
                await client.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(client)
            except Exception as e:
                logger.error(f"Broadcast error on topic '{topic}': {e}")
                disconnected.append(client)

        if disconnected:
            await self._cleanup_disconnected(disconnected)

    async def _heartbeat_loop(self, websocket: WebSocket) -> None:
        try:
            while True:
                await asyncio.sleep(self._heartbeat_interval)
                await websocket.send_json({"type": "ping"})
        except (WebSocketDisconnect, asyncio.CancelledError):
            pass
        except Exception as e:
            logger.warning(f"Heartbeat failed: {e}")

    def _cancel_heartbeat(self, websocket: WebSocket) -> None:
        task = self._heartbeat_tasks.pop(websocket, None)
        if task and not task.done():
            task.cancel()

    async def _cleanup_disconnected(self, clients: list[WebSocket]) -> None:
        async with self._lock:
            for topic in list(self._connections.keys()):
                for client in clients:
                    self._connections[topic].discard(client)
                    self._heartbeat_tasks.pop(client, None)
                if not self._connections[topic]:
                    del self._connections[topic]