import hashlib
import hmac

from app.config import settings


def verify_github_signature(raw_body: bytes, signature: str | None) -> bool:
    """Verify the GitHub webhook signature using the shared secret.

    GitHub sends a SHA-256 HMAC signature in the X-Hub-Signature-256 header.
    The value must match the payload produced using the configured webhook secret.
    """
    if not signature:
        return False

    expected = "sha256=" + hmac.new(
        settings.github_webhook_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)
