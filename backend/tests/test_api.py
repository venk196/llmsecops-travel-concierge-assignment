from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_uses_mock_provider(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "mock")
    response = client.post("/chat", json={"prompt": "Plan a weekend in Singapore"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["route"] in {"fast", "quality"}
    assert payload["trace_id"]


def test_chat_blocks_unconfirmed_action():
    response = client.post("/chat", json={"prompt": "Book it", "requested_action": "book hotel"})
    assert response.status_code == 400

