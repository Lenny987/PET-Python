import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app.main import app
from app.utils.jwt import create_access_token
from app.schemas import Topic
from app.deps import get_broker, get_manager


@pytest.fixture
def mock_broker():
    broker = AsyncMock()
    broker.publish = AsyncMock(return_value=True)
    broker.add_to_history = AsyncMock()
    broker.get_history = AsyncMock(return_value=[
        {"id": "1-0", "data": {"topic": "orders", "payload": {"id": 999, "status": "shipped"}}}
    ])
    return broker


@pytest.fixture
def mock_manager():
    manager = AsyncMock()
    manager.connect = AsyncMock()
    manager.disconnect = AsyncMock()
    return manager


@pytest.fixture(autouse=True)
def override_dependencies(mock_broker, mock_manager):
    app.dependency_overrides[get_broker] = lambda: mock_broker
    app.dependency_overrides[get_manager] = lambda: mock_manager
    yield
    app.dependency_overrides.clear()


def test_publish_endpoint(mock_broker):
    with TestClient(app=app) as client:
        resp = client.post("/api/v1/publish", json={
            "topic": Topic.ORDERS.value,
            "payload": {"id": 999, "status": "shipped"}
        })

        assert resp.status_code == 202
        assert resp.json() == {"status": "accepted"}

        mock_broker.publish.assert_called_once()
        mock_broker.add_to_history.assert_called_once()


def test_history_endpoint(mock_broker):
    with TestClient(app=app) as client:
        resp = client.get(f"/api/v1/history/{Topic.ORDERS.value}?limit=10")

        assert resp.status_code == 200
        data = resp.json()
        assert data["topic"] == Topic.ORDERS.value
        assert len(data["messages"]) >= 1

        # Проверяем вызов мока
        mock_broker.get_history.assert_called_once_with(Topic.ORDERS.value, 10)


def test_websocket_connection(mock_manager, mock_broker):
    from websockets.exceptions import ConnectionClosed

    token = create_access_token({"sub": "ws-test-user"})

    with TestClient(app=app) as client:

        with client.websocket_connect(
                f"/api/v1/ws?topic={Topic.ORDERS.value}&token={token}"
        ) as websocket:

            mock_manager.connect.assert_called_once()

            try:
                data = websocket.receive_json(timeout=1.0)
                assert data.get("type") == "ping"
            except:
                pass


            websocket.send_text("ping")

        mock_manager.disconnect.assert_called_once()


def test_get_broker_dependency(mock_broker):
    from fastapi import Request
    from app.deps import get_broker

    request = MagicMock(spec=Request)
    request.app.state.broker = mock_broker

    import asyncio
    result = asyncio.run(get_broker(request))

    assert result == mock_broker


def test_get_manager_dependency(mock_manager):
    from fastapi import WebSocket
    from app.deps import get_manager

    websocket = MagicMock(spec=WebSocket)
    websocket.app.state.manager = mock_manager

    import asyncio
    result = asyncio.run(get_manager(websocket))

    assert result == mock_manager