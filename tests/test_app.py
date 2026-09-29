from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home():
    assert client.get("/").status_code == 200

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"

def test_users_api():
    assert client.get("/api/users").status_code == 200
