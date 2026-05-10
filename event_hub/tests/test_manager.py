import asyncio
import pytest
from unittest.mock import AsyncMock
from fastapi import WebSocketDisconnect
from app.connection_manager import ConnectionManager

@pytest.fixture
def manager():
    return ConnectionManager(heartbeat_interval=1)  # Ускоренный heartbeat для тестов

@pytest.mark.asyncio
async def test_connect_and_disconnect(manager: ConnectionManager):
    ws = AsyncMock()
    await manager.connect(ws, "orders")
    assert "orders" in manager._connections
    assert ws in manager._connections["orders"]

    await manager.disconnect(ws, "orders")
    assert "orders" not in manager._connections

@pytest.mark.asyncio
async def test_broadcast_success(manager: ConnectionManager):
    ws1, ws2 = AsyncMock(), AsyncMock()
    await manager.connect(ws1, "orders")
    await manager.connect(ws2, "orders")

    await manager.broadcast("orders", {"event": "test"})
    ws1.send_json.assert_called_once_with({"event": "test"})
    ws2.send_json.assert_called_once_with({"event": "test"})

@pytest.mark.asyncio
async def test_broadcast_handles_disconnect(manager: ConnectionManager):
    ws = AsyncMock()
    ws.send_json.side_effect = WebSocketDisconnect()
    await manager.connect(ws, "orders")

    await manager.broadcast("orders", {"event": "fail"})
    # Клиент должен быть удалён из структуры
    assert "orders" not in manager._connections
    assert ws not in manager._heartbeat_tasks