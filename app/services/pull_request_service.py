from __future__ import annotations

from app.db.database import SessionLocal
from app.db.repositories import PullRequestRepository
from app.github.client import GitHubClient


class PullRequestService:
    """Service responsible for storing basic PR metadata after a GitHub webhook."""

    def __init__(self):
        self.client = GitHubClient()

    def process_pull_request_event(self, *, repository_id: int, repository_name: str, pr_number: int,
                                  owner: str, repo: str, installation_id: int | None = None,
                                  token: str | None = None) -> dict:
        if token is not None:
            self.client = GitHubClient(token=token)
        elif installation_id is not None:
            self.client = GitHubClient(token=self.client.get_installation_token(installation_id))

        pr_data = self.client.get_pull_request(owner, repo, pr_number)
        changed_files = self.client.get_changed_files(owner, repo, pr_number)

        with SessionLocal() as db:
            repository = PullRequestRepository(db)
            saved = repository.create(
                repository_id=repository_id,
                repository_name=repository_name,
                pr_number=pr_number,
                author=pr_data["author"] or "unknown",
                action="opened",
                base_branch=pr_data["base_branch"] or "unknown",
                head_branch=pr_data["head_branch"] or "unknown",
                head_sha=pr_data["head_sha"] or "unknown",
            )

        return {
            "pr_number": pr_number,
            "repository": repository_name,
            "author": pr_data["author"],
            "base_branch": pr_data["base_branch"],
            "head_branch": pr_data["head_branch"],
            "head_sha": pr_data["head_sha"],
            "changed_files": len(changed_files),
            "saved_id": saved.id,
        }
