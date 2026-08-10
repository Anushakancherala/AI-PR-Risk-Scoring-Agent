from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint_returns_healthy() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint_returns_service_status() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["app"] == "pr-risk-agent"
    assert response.json()["status"] == "running"
