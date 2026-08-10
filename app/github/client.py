from __future__ import annotations

import httpx

from app.config import settings
from app.github.auth import create_app_jwt


class GitHubClient:
    """Small GitHub REST client used for GitHub App auth and PR fetches."""

    def __init__(self, token: str | None = None, base_url: str = "https://api.github.com"):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def get_installation_token(self, installation_id: int) -> str:
        """Exchange the app JWT for an installation access token."""
        app_jwt = create_app_jwt()
        url = f"{self.base_url}/app/installations/{installation_id}/access_tokens"
        response = httpx.post(
            url,
            headers={
                "Authorization": f"Bearer {app_jwt}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            json={},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data["token"]

    def get_pull_request(self, owner: str, repo: str, pr_number: int) -> dict:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        response = self._get(url)
        payload = response.json()

        return {
            "number": payload.get("number"),
            "title": payload.get("title"),
            "body": payload.get("body"),
            "author": payload.get("user", {}).get("login"),
            "base_branch": payload.get("base", {}).get("ref"),
            "head_branch": payload.get("head", {}).get("ref"),
            "base_sha": payload.get("base", {}).get("sha"),
            "head_sha": payload.get("head", {}).get("sha"),
            "state": payload.get("state"),
            "html_url": payload.get("html_url"),
        }

    def get_changed_files(self, owner: str, repo: str, pr_number: int) -> list[dict]:
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        response = self._get(url)
        return response.json()

    def _get(self, url: str) -> httpx.Response:
        if not self.token:
            raise ValueError("A GitHub token is required for client requests.")

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        response = httpx.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response
