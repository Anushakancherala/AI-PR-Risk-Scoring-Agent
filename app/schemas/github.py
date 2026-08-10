from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class GitHubRepositoryPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int | None = None
    full_name: str | None = None
    name: str | None = None


class GitHubUserPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    login: str | None = None


class GitHubPullRequestPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    number: int | None = None
    title: str | None = None
    body: str | None = None
    state: str | None = None
    user: GitHubUserPayload | None = None
    base: dict[str, Any] | None = None
    head: dict[str, Any] | None = None
    html_url: str | None = None
    merged: bool | None = None


class PullRequestEventPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    action: str | None = None
    repository: GitHubRepositoryPayload | None = None
    pull_request: GitHubPullRequestPayload | None = None
    installation: dict[str, Any] | None = Field(default_factory=dict)
    sender: GitHubUserPayload | None = None
