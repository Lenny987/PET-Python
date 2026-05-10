from enum import Enum
from pydantic import BaseModel, Field
from typing import Any
from datetime import datetime, timezone

class Topic(str, Enum):
    ORDERS = "orders"
    USERS = "users"
    NOTIFICATIONS = "notofocations"
    SYSTEM = "system"

class EventMessage(BaseModel):
    topic: Topic
    payload: dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class HistoryItem(BaseModel):
    id: str
    data: dict[str, Any]

class HistoryResponse(BaseModel):
    topic: str
    messages: list[HistoryItem]