from app.github.client import GitHubClient


class DummyResponse:
    def __init__(self, *, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def test_get_installation_token_uses_installation_id(monkeypatch):
    captured = {}

    def fake_post(url, *, headers, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["json"] = json
        captured["timeout"] = timeout
        return DummyResponse(payload={"token": "test-token"})

    monkeypatch.setattr("app.github.client.httpx.post", fake_post)
    monkeypatch.setattr("app.github.client.create_app_jwt", lambda: "jwt-token")

    client = GitHubClient()
    token = client.get_installation_token(123)

    assert token == "test-token"
    assert captured["url"].endswith("/app/installations/123/access_tokens")
    assert captured["headers"]["Authorization"] == "Bearer jwt-token"


def test_get_pr_metadata_returns_expected_fields(monkeypatch):
    def fake_get(url, *, headers, timeout=None):
        assert url.endswith("/repos/octocat/demo-repo/pulls/7")
        assert headers["Authorization"] == "Bearer token-abc"
        assert timeout == 30
        return DummyResponse(
            payload={
                "number": 7,
                "title": "Refactor auth",
                "body": "Some description",
                "user": {"login": "octocat"},
                "base": {"ref": "main", "sha": "base-sha"},
                "head": {"ref": "feature/auth", "sha": "head-sha"},
            }
        )

    monkeypatch.setattr("app.github.client.httpx.get", fake_get)

    client = GitHubClient(token="token-abc")
    pr = client.get_pull_request("octocat", "demo-repo", 7)

    assert pr["number"] == 7
    assert pr["title"] == "Refactor auth"
    assert pr["author"] == "octocat"
    assert pr["base_branch"] == "main"
    assert pr["head_branch"] == "feature/auth"
    assert pr["head_sha"] == "head-sha"


def test_get_changed_files_returns_pr_file_list(monkeypatch):
    def fake_get(url, *, headers, timeout=None):
        assert url.endswith("/repos/octocat/demo-repo/pulls/7/files")
        assert timeout == 30
        return DummyResponse(
            payload=[
                {"filename": "app/auth.py", "additions": 10, "deletions": 2, "status": "modified"},
                {"filename": "app/main.py", "additions": 5, "deletions": 1, "status": "modified"},
            ]
        )

    monkeypatch.setattr("app.github.client.httpx.get", fake_get)

    client = GitHubClient(token="token-abc")
    files = client.get_changed_files("octocat", "demo-repo", 7)

    assert len(files) == 2
    assert files[0]["filename"] == "app/auth.py"
    assert files[0]["additions"] == 10
