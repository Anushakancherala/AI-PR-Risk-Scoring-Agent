import time

import jwt

from app.config import settings


def create_app_jwt() -> str:
    """Create a GitHub App JWT used to authenticate as the application itself."""
    if settings.github_app_id is None:
        raise ValueError("GITHUB_APP_ID must be set to create a GitHub App JWT.")

    if not settings.github_private_key:
        raise ValueError("GITHUB_PRIVATE_KEY must be set to create a GitHub App JWT.")

    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + 600,
        "iss": settings.github_app_id,
    }
    return jwt.encode(payload, settings.github_private_key, algorithm="RS256")
