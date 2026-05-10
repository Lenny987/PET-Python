from typing import TYPE_CHECKING
from fastapi import APIRouter, Depends, WebSocket, HTTPException, Query
from fastapi.responses import JSONResponse
from app.schemas import EventMessage, Topic, HistoryResponse
from app.deps import get_token_from_ws, get_broker, get_manager

if TYPE_CHECKING:
    from app.redis_client import RedisBroker
    from app.connection_manager import ConnectionManager

router = APIRouter(prefix="/api/v1")

@router.post("/publish")
async def publish_event(
    event: EventMessage,
    broker: "RedisBroker" = Depends(get_broker)
):
    success = await broker.publish(event.topic, event)
    if success:
        await broker.add_to_history(event.topic.value, event)
        return JSONResponse(status_code=202, content={"status": "accepted"})
    raise HTTPException(status_code=503, detail="Redis unavailable")

@router.get("/history/{topic}")
async def get_history(
    topic: Topic,
    limit: int = Query(default=50, le=100),
    broker: "RedisBroker" = Depends(get_broker)
):
    messages = await broker.get_history(topic.value, limit)
    return HistoryResponse(topic=topic.value, messages=messages)

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    topic: Topic = Query(...),
    _token_payload: dict = Depends(get_token_from_ws),
    manager: "ConnectionManager" = Depends(get_manager)
):
    await websocket.accept()
    try:
        await manager.connect(websocket, topic.value)
        while True:
            await websocket.receive_text()
    except Exception as e:
        print(f"WS Error: {e}")
    finally:
        await manager.disconnect(websocket, topic.value)