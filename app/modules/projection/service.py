# app/modules/projection/service.py

from fastapi import WebSocket
import json

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        await websocket.send_text(message)

    async def broadcast(self, message: str) -> None:
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

class ProjectionService:
    def __init__(self, manager: ConnectionManager) -> None:
        self.manager = manager

    async def update_screen(self, projection_dict: dict) -> None:
        await self.manager.broadcast(json.dumps(projection_dict))

    async def connect(self, websocket: WebSocket) -> None:
        await self.manager.connect(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        await self.manager.disconnect(websocket)

manager = ConnectionManager()
