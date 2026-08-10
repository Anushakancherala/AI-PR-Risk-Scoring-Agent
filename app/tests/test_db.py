from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db.models import PullRequest


def test_pull_request_model_can_be_created_and_inserted() -> None:
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as session:
        pr = PullRequest(
            repository_id=42,
            repository_name="demo/repo",
            pr_number=7,
            author="octocat",
            action="opened",
            base_branch="main",
            head_branch="feature/test",
            head_sha="abc123",
        )
        session.add(pr)
        session.commit()

        stored = session.query(PullRequest).filter_by(pr_number=7).one()
        assert stored.repository_name == "demo/repo"
        assert stored.author == "octocat"
        assert stored.action == "opened"
