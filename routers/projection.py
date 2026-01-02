from fastapi import WebSocket, WebSocketDisconnect, APIRouter, HTTPException, status, Depends
from auth.dependencies import require_admin
from schemas import Projection
from typing import Any
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"New connection. Total connections: {len(self.active_connections)}")
        
    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
        
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                disconnected.append(connection)
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)
    
manager = ConnectionManager()

@router.post('/projection/{council_id}', status_code=status.HTTP_200_OK)
async def update_screen(council_id: int, projection: Projection) -> dict[str, Any]:
    projection_dict = projection.model_dump(exclude_unset=True)
    print(projection_dict)
    await manager.broadcast(json.dumps(projection_dict))
    return {"message": "success", "projection": projection_dict}

@router.websocket("/screen")
async def screen_connection(websocket: WebSocket):
    await manager.connect(websocket)
    try: 
        while True:
            data = await websocket.receive_text() # needed to handle disconnects            
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
