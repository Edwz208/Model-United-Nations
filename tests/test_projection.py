# tests/test_projection.py

from fastapi.testclient import TestClient
from main import app

def test_screen_connection():
    client = TestClient(app)

    with client.websocket_connect("/projection/18/screen") as websocket:
        client.post("/projection/18", json={"active_screen": "conference"})
        data = websocket.receive_json()

    assert data == {"active_screen": "conference"}
