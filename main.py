from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from routers import countryData, login, resolutionsData, amendmentsData
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv, find_dotenv
from db import get_async_pool
from contextlib import asynccontextmanager
import asyncio  
import authentication
from authentication import get_current_user
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)
from fastapi.staticfiles import StaticFiles
from typing import List
import json


origins = [
    "http://localhost:8000",
    "http://localhost:5173",
]   

async def check_async_connections():
    while True:
        await asyncio.sleep(600)
        print("check async connections health")
        await get_async_pool().check()
        
@asynccontextmanager # Async context manager allows for an async function to set up and remove resources upon startup and shutdown
async def lifespan_handler(app: FastAPI):
    await get_async_pool().open()
    
    task = asyncio.create_task(check_async_connections()) # background task that constantly occurs, at the same time as other event based tasks
    yield # pause here until the app is shutting down
    task.cancel()
    await get_async_pool().close()

app = FastAPI(lifespan=lifespan_handler)
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
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
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try: 
        while True:
            data = await websocket.receive_text()
            token = data.get("accessToken")
            payload = get_current_user(token)
            if payload.get("role") == 4015:
                message = {"message": data}
                manager.broadcast(json.dumps(message))
            else:
                manager.send_personal_message({"accessToken": False})
                
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    
    
    
app.mount("/resolutions-pdfs", StaticFiles(directory="uploads/resolutions"), name="pdfs") # served from localhost80000 because server

app.include_router(login.router)
app.include_router(countryData.router)
app.include_router(resolutionsData.router)
app.include_router(amendmentsData.router)
