from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_listar_activos():
    # 1. Registro
    client.post("/registro", json={"username": "test_user", "password": "test123"})
    
    # 2. Login
    response = client.post("/login", data={"username": "test_user", "password": "test123"})
    token = response.json()["access_token"]
    
    # 3. Request con token
    response = client.get("/activos", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200