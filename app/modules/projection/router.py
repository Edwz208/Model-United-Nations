# app/modules/projection/router.py

from fastapi import WebSocket, WebSocketDisconnect, APIRouter, status, Depends
from typing import Any
from app.modules.projection.schemas import Projection
from app.modules.projection.service import ProjectionService, manager

router = APIRouter(prefix="/projection", tags=["projection"])

def get_projection_service() -> ProjectionService:
    return ProjectionService(manager)

@router.post('/{council_id}', status_code=status.HTTP_200_OK)
async def update_screen(council_id: int, projection: Projection, service: ProjectionService = Depends(get_projection_service)) -> dict[str, Any]:
    projection_dict = projection.model_dump(exclude_unset=True)
    await service.update_screen(projection_dict)
    return {"message": "success", "projection": projection_dict}

@router.websocket("/{council_id}/screen")
async def connect_screen(council_id: int, websocket: WebSocket, service: ProjectionService = Depends(get_projection_service)) -> None:
    try:
        await service.connect(websocket)
    except Exception:
        return

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await service.disconnect(websocket)
