import hashlib
import hmac
import json

from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

client = TestClient(app)


def build_signed_payload(payload: dict, secret: str) -> tuple[bytes, str]:
    body = json.dumps(payload).encode("utf-8")
    signature = "sha256=" + hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return body, signature


def test_valid_signature_allows_pull_request_event() -> None:
    payload = {
        "action": "opened",
        "repository": {"id": 1, "full_name": "octocat/demo-repo", "name": "demo-repo"},
        "pull_request": {
            "number": 12,
            "title": "Fix login bug",
            "body": "Test PR",
            "state": "open",
            "user": {"login": "octocat"},
            "base": {"ref": "main", "sha": "base-sha"},
            "head": {"ref": "feature/test", "sha": "head-sha"},
        },
    }
    body, signature = build_signed_payload(payload, settings.github_webhook_secret)

    response = client.post(
        "/webhooks/github",
        content=body,
        headers={
            "X-GitHub-Event": "pull_request",
            "X-Hub-Signature-256": signature,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "accepted"
    assert response.json()["pr_number"] == 12


def test_invalid_signature_is_rejected() -> None:
    payload = {"action": "opened"}
    body = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/webhooks/github",
        content=body,
        headers={
            "X-GitHub-Event": "pull_request",
            "X-Hub-Signature-256": "sha256=invalid",
        },
    )

    assert response.status_code == 401
    assert "Invalid GitHub webhook signature" in response.json()["detail"]


def test_missing_signature_is_rejected() -> None:
    payload = {"action": "opened"}
    body = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/webhooks/github",
        content=body,
        headers={"X-GitHub-Event": "pull_request"},
    )

    assert response.status_code == 401


def test_unsupported_event_type_is_ignored() -> None:
    payload = {"action": "created"}
    body, signature = build_signed_payload(payload, settings.github_webhook_secret)

    response = client.post(
        "/webhooks/github",
        content=body,
        headers={
            "X-GitHub-Event": "push",
            "X-Hub-Signature-256": signature,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ignored"
