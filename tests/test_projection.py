from fastapi.testclient import TestClient
from auth.dependencies import require_admin
from main import app

def fake_require_admin():
    return {"message": "success"}

def test_screen_connection():
    app.dependency_overrides[require_admin] = fake_require_admin
    client = TestClient(app)
    client2 = TestClient(app)

    with client.websocket_connect("/ws") as websocket:
        response2 = client2.post('/projection/18', json={"active_screen": "conference"})
        data = websocket.receive_json() # no need to await, the testclient handles already event loop
        # receive_json simply outputs latest message 
    
    assert data == {"active_screen": "conference"}
