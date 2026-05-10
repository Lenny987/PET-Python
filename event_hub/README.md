# 🚀 Real-time Event Hub

WebSocket-брокер для подписки, публикации и маршрутизации событий в реальном времени.

## 🏗 Архитектура
```mermaid
graph LR
    A[Клиент] -->|POST /publish| B(FastAPI)
    C[Клиент] -->|WS /ws?topic=...| B
    B -->|Redis Pub/Sub| D[(Redis)]
    B -->|Redis Streams| D
    D -->|Сообщения| B
    B -->|JSON| C