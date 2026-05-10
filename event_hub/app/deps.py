from typing import TYPE_CHECKING
from fastapi import Depends, Request, WebSocket, Query
from app.utils.jwt import verify_token

if TYPE_CHECKING:
    from app.redis_client import RedisBroker
    from app.connection_manager import ConnectionManager

async def get_token_from_ws(
    websocket: WebSocket,
    token: str = Query(...),
) -> dict:
    payload = verify_token(token)
    if not payload:
        await websocket.close(code=1008, reason="Invalid token")
        return {}
    return payload

async def get_broker(request: Request) -> "RedisBroker":
    return request.app.state.broker

async def get_manager(websocket: WebSocket) -> "ConnectionManager":
    return websocket.app.state.manager