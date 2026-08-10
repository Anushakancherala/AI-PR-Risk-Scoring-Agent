from sqlalchemy.orm import Session

from app.db.models import PullRequest


class PullRequestRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, *, repository_id: int, repository_name: str, pr_number: int, author: str,
               action: str, base_branch: str, head_branch: str, head_sha: str) -> PullRequest:
        pull_request = PullRequest(
            repository_id=repository_id,
            repository_name=repository_name,
            pr_number=pr_number,
            author=author,
            action=action,
            base_branch=base_branch,
            head_branch=head_branch,
            head_sha=head_sha,
        )
        self.db.add(pull_request)
        self.db.commit()
        self.db.refresh(pull_request)
        return pull_request

    def get_by_repository_and_pr_number(self, *, repository_id: int, pr_number: int) -> PullRequest | None:
        return (
            self.db.query(PullRequest)
            .filter(PullRequest.repository_id == repository_id)
            .filter(PullRequest.pr_number == pr_number)
            .order_by(PullRequest.id.desc())
            .first()
        )
