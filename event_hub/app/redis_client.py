import asyncio
import json
import logging
from typing import Any
from redis.asyncio import Redis
from redis.exceptions import ConnectionError, RedisError

from app.config import settings
from app.schemas import EventMessage

logger = logging.getLogger(__name__)


class RedisBroker:
    def __init__(self, redis: Redis, connection_manager=None) -> None:
        self._redis = redis
        self._connection_manager = connection_manager
        self._retry_queue: asyncio.Queue[tuple[str, str]] = asyncio.Queue()
        self._retry_task: asyncio.Task[None] | None = None
        self._pubsub_task: asyncio.Task[None] | None = None
        self._pubsub = None

    async def start(self) -> None:
        self._retry_task = asyncio.create_task(self._process_retry_queue())

        self._pubsub = self._redis.pubsub()
        await self._pubsub.psubscribe("events:*")

        self._pubsub_task = asyncio.create_task(self._listen_to_pubsub())

    async def stop(self) -> None:
        if self._pubsub_task and not self._pubsub_task.done():
            self._pubsub_task.cancel()
            try:
                await self._pubsub_task
            except asyncio.CancelledError:
                pass

        if self._retry_task and not self._retry_task.done():
            self._retry_task.cancel()
            try:
                await self._retry_task
            except asyncio.CancelledError:
                pass

        if self._pubsub:
            await self._pubsub.punsubscribe()
            await self._pubsub.close()

        await self._redis.aclose()

    async def _listen_to_pubsub(self) -> None:
        try:
            while True:

                message = await self._pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0
                )

                if message and message["type"] == "pmessage":
                    channel = message["channel"]
                    data = message["data"]

                    if isinstance(channel, bytes):
                        channel = channel.decode()
                    if isinstance(data, bytes):
                        data = data.decode()

                    if channel.startswith("events:"):
                        topic = channel.split(":", 1)[1]

                        topic_str = topic.value if hasattr(topic, 'value') else str(topic)

                        if topic_str.startswith("Topic."):
                            topic_str = topic_str.split("Topic.", 1)[1].lower()
                        try:
                            payload = json.loads(data)
                            if self._connection_manager:
                                await self._connection_manager.broadcast(topic_str, payload)
                                logger.info(f"Broadcasted to topic '{topic}': {payload.get('payload', {})}")
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse message from {channel}: {e}")

        except asyncio.CancelledError:
            logger.info("Pub/Sub listener stopped")
        except Exception as e:
            logger.error(f"Pub/Sub listener error: {e}")

    async def publish(self, topic: str, message: EventMessage) -> bool:
        data = message.model_dump_json()
        channel = f"events:{topic}"
        try:
            await asyncio.wait_for(self._redis.publish(channel, data), timeout=2.0)
            return True
        except (ConnectionError, TimeoutError, RedisError) as e:
            logger.error(f"Redis publish failed for '{topic}': {e}")
            await self._retry_queue.put((channel, data))
            return False

    async def add_to_history(self, topic: str, message: EventMessage) -> bool:
        data = message.model_dump_json()
        try:
            await self._redis.xadd(
                f"stream:{topic}", {"data": data}, maxlen=settings.max_history_length
            )
            return True
        except (ConnectionError, RedisError) as e:
            logger.error(f"Redis XADD failed for '{topic}': {e}")
            return False

    async def get_history(self, topic: str, limit: int = settings.max_history_length) -> list[dict[str, Any]]:
        try:
            raw = await self._redis.xrevrange(f"stream:{topic}", count=limit)
            return [
                {"id": msg_id, "data": json.loads(msg.get("data", "{}"))}
                for msg_id, msg in raw
            ]
        except (ConnectionError, RedisError) as e:
            logger.error(f"Redis XREVRANGE failed for '{topic}': {e}")
            return []

    async def _process_retry_queue(self) -> None:
        while True:
            try:
                channel, data = await self._retry_queue.get()
                for attempt in range(settings.redis_retry_max):
                    try:
                        await self._redis.publish(channel, data)
                        logger.info(f"Retried publish to {channel} successfully")
                        break
                    except Exception as e:
                        logger.warning(f"Retry {attempt + 1} failed for {channel}: {e}")
                        await asyncio.sleep(2 ** attempt)
                self._retry_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Retry queue error: {e}")
                await asyncio.sleep(1)