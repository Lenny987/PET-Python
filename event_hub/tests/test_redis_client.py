import pytest
import json
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from redis.exceptions import ConnectionError, RedisError
from app.redis_client import RedisBroker
from app.schemas import EventMessage, Topic


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.pubsub = MagicMock(return_value=AsyncMock())
    return redis


@pytest.fixture
def broker(mock_redis):
    return RedisBroker(mock_redis)


@pytest.mark.asyncio
async def test_publish_success(broker, mock_redis):
    event = EventMessage(topic=Topic.ORDERS, payload={"id": 1})

    result = await broker.publish(Topic.ORDERS.value, event)

    assert result is True
    mock_redis.publish.assert_called_once()


@pytest.mark.asyncio
async def test_publish_redis_error_goes_to_retry(broker, mock_redis):
    mock_redis.publish.side_effect = ConnectionError("Redis down")

    event = EventMessage(topic=Topic.ORDERS, payload={"id": 2})
    result = await broker.publish(Topic.ORDERS.value, event)

    assert result is False
    assert broker._retry_queue.qsize() == 1

    channel, data = await broker._retry_queue.get()
    assert channel == "events:orders"
    assert json.loads(data)["payload"]["id"] == 2


@pytest.mark.asyncio
async def test_add_to_history_success(broker, mock_redis):
    event = EventMessage(topic=Topic.ORDERS, payload={"id": 3})

    result = await broker.add_to_history(Topic.ORDERS.value, event)

    assert result is True
    mock_redis.xadd.assert_called_once()


@pytest.mark.asyncio
async def test_add_to_history_redis_error(broker, mock_redis):
    mock_redis.xadd.side_effect = RedisError("Stream error")

    event = EventMessage(topic=Topic.ORDERS, payload={"id": 4})
    result = await broker.add_to_history(Topic.ORDERS.value, event)

    assert result is False


@pytest.mark.asyncio
async def test_get_history_success(broker, mock_redis):
    mock_redis.xrevrange.return_value = [
        ("1715450000000-0", {"data": json.dumps({"topic": "orders", "payload": {"id": 5}})}),
        ("1715449000000-0", {"data": json.dumps({"topic": "orders", "payload": {"id": 4}})}),
    ]

    result = await broker.get_history(Topic.ORDERS.value, limit=10)

    assert len(result) == 2
    assert result[0]["data"]["payload"]["id"] == 5
    mock_redis.xrevrange.assert_called_once_with("stream:orders", count=10)


@pytest.mark.asyncio
async def test_get_history_redis_error(broker, mock_redis):
    mock_redis.xrevrange.side_effect = ConnectionError("Redis down")

    result = await broker.get_history(Topic.ORDERS.value, limit=10)

    assert result == []


@pytest.mark.asyncio
async def test_process_retry_queue_success(broker, mock_redis):
    await broker._retry_queue.put(("events:users", '{"test": "retry"}'))

    task = asyncio.create_task(broker._process_retry_queue())

    await asyncio.sleep(0.1)

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    mock_redis.publish.assert_called()