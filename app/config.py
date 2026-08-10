import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


@dataclass
class Settings:
    app_name: str = "pr-risk-agent"
    app_version: str = "0.1.0"
    github_app_id: Optional[int] = None
    github_private_key: str = ""
    github_webhook_secret: str = ""
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/pr_risk_agent"

    @classmethod
    def from_env(cls) -> "Settings":
        raw_app_id = os.getenv("GITHUB_APP_ID", "")
        github_app_id = int(raw_app_id) if raw_app_id else None

        return cls(
            app_name=os.getenv("APP_NAME", "pr-risk-agent"),
            app_version=os.getenv("APP_VERSION", "0.1.0"),
            github_app_id=github_app_id,
            github_private_key=os.getenv("GITHUB_PRIVATE_KEY", ""),
            github_webhook_secret=os.getenv("GITHUB_WEBHOOK_SECRET", ""),
            database_url=os.getenv(
                "DATABASE_URL",
                "postgresql+psycopg://postgres:postgres@localhost:5432/pr_risk_agent",
            ),
        )

    def validate(self) -> None:
        missing = []

        if not self.github_webhook_secret:
            missing.append("GITHUB_WEBHOOK_SECRET")
        if not self.database_url:
            missing.append("DATABASE_URL")

        if missing:
            raise ValueError(
                "Missing required environment variables: " + ", ".join(missing)
            )


settings = Settings.from_env()
