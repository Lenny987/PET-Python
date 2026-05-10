from fastapi import FastAPI
from contextlib import asynccontextmanager
from redis.asyncio import Redis
import logging

from app.config import settings
from app.redis_client import RedisBroker
from app.connection_manager import ConnectionManager
from app.routers import router
from app.docs import get_custom_swagger_ui_html

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    manager = ConnectionManager(heartbeat_interval=settings.heartbeat_interval)
    broker = RedisBroker(redis, connection_manager=manager)

    await broker.start()

    app.state.broker = broker
    app.state.manager = manager

    logging.info("✅ Application started")
    yield

    logging.info("🛑 Shutting down...")
    await broker.stop()
    for topic in list(manager._connections.keys()):
        for ws in list(manager._connections[topic]):
            await manager.disconnect(ws, topic)
    logging.info("Application stoped")

app = FastAPI(lifespan=lifespan)
app.include_router(router)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_custom_swagger_ui_html(
        openapi_url="/openapi.json",
        title="Event Hub API",
    )