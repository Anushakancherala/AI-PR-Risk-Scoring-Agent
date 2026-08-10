import hashlib
import hmac
import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.db.models import GitHubDelivery
from app.main import app

client = TestClient(app)


def build_signed_payload(payload: dict, secret: str) -> tuple[bytes, str]:
    body = json.dumps(payload).encode("utf-8")
    signature = "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return body, signature


def test_duplicate_delivery_is_rejected(monkeypatch):
    secret = "test-secret"
    payload = {
        "action": "opened",
        "repository": {"id": 1, "full_name": "octocat/demo-repo", "name": "demo-repo"},
        "pull_request": {
            "number": 12,
            "title": "Fix login bug",
            "state": "open",
            "user": {"login": "octocat"},
            "base": {"ref": "main", "sha": "base-sha"},
            "head": {"ref": "feature/test", "sha": "head-sha"},
        },
    }
    body, signature = build_signed_payload(payload, secret)

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr("app.utils.security.settings.github_webhook_secret", secret)
    monkeypatch.setattr("app.api.routes.webhooks.SessionLocal", TestSessionLocal)

    headers = {
        "X-GitHub-Event": "pull_request",
        "X-Hub-Signature-256": signature,
        "X-GitHub-Delivery": "duplicate-123",
    }

    first = client.post("/webhooks/github", content=body, headers=headers)
    second = client.post("/webhooks/github", content=body, headers=headers)

    assert first.status_code == 200
    assert first.json()["status"] == "accepted"
    assert second.status_code == 200
    assert second.json()["status"] == "duplicate"

    with TestSessionLocal() as db:
        count = db.query(GitHubDelivery).filter(GitHubDelivery.delivery_id == "duplicate-123").count()
        assert count == 1
