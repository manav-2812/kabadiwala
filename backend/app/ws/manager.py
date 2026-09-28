from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.channel_subscriptions: dict[str, set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "global"):
        await websocket.accept()
        self.active_connections.append(websocket)
        if channel not in self.channel_subscriptions:
            self.channel_subscriptions[channel] = set()
        self.channel_subscriptions[channel].add(websocket)

    def disconnect(self, websocket: WebSocket, channel: str = "global"):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if channel in self.channel_subscriptions and websocket in self.channel_subscriptions[channel]:
            self.channel_subscriptions[channel].remove(websocket)

    async def broadcast(self, message: dict[str, Any], channel: str = "global"):
        subscribers = self.channel_subscriptions.get(channel, set()).copy()
        dead = []
        for connection in subscribers:
            try:
                await connection.send_json(message)
            except Exception:
                dead.append(connection)
        for d in dead:
            self.disconnect(d, channel)

ws_manager = ConnectionManager()
