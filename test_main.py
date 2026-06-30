from fastapi.testclient import TestClient
from main import app
from datetime import datetime, timezone

client = TestClient(app)

def test_login_correcto():
    client.post("/registro", json={"username": "test_login", "password": "test123"})
    response = client.post("/login", data={"username": "test_login", "password": "test123"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_incorrecto():
    response = client.post("/login", data={"username": "noexiste", "password": "mal"})
    assert response.status_code == 401

def test_crear_activo():
    client.post("/registro", json={"username": "test_crear", "password": "test123"})

    response = client.post("/login", data={"username": "test_crear", "password": "test123"})
    token = response.json()["access_token"]

    response = client.post("/activos", headers={"Authorization": f"Bearer {token}"}, json={"ticker": "MAIN", "nombre": "Main Street Capital"})
    assert response.status_code == 200


def test_listar_activos():
    # 1. Registro
    client.post("/registro", json={"username": "test_user", "password": "test123"})
    
    # 2. Login
    response = client.post("/login", data={"username": "test_user", "password": "test123"})
    token = response.json()["access_token"]
    
    # 3. Request con token
    response = client.get("/activos", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

def test_crear_compra():
    client.post("/registro", json={"username": "test_crear", "password": "test123"})

    response = client.post("/login", data={"username": "test_crear", "password": "test123"})
    token = response.json()["access_token"]

    response = client.post("/activos", headers={"Authorization": f"Bearer {token}"}, json={"ticker": "MAIN", "nombre": "Main Street Capital"})

    response = client.post("/compras", headers={"Authorization": f"Bearer {token}"}, json={"activo_id": 1, "fecha_compra": "2026-06-25", "precio": 55, "cantidad": 4, "tipo_cambio": 1.16})
    assert response.status_code == 200
