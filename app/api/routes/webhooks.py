import json
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.db.database import SessionLocal
from app.db.models import GitHubDelivery
from app.schemas.github import PullRequestEventPayload
from app.utils.logging import configure_logging
from app.utils.security import verify_github_signature

logger = configure_logging()

router = APIRouter(tags=["github-webhooks"])
SUPPORTED_PR_ACTIONS = {"opened", "synchronize", "reopened", "closed"}


@router.post("/webhooks/github", summary="Receive GitHub webhook events")
async def github_webhook(request: Request) -> dict[str, Any]:
    raw_body = await request.body()
    event_type = request.headers.get("X-GitHub-Event")
    signature = request.headers.get("X-Hub-Signature-256")
    delivery_id = request.headers.get("X-GitHub-Delivery")

    if not event_type:
        raise HTTPException(status_code=400, detail="Missing X-GitHub-Event header")

    if not signature:
        raise HTTPException(status_code=401, detail="Missing GitHub webhook signature")

    if not verify_github_signature(raw_body, signature):
        logger.warning(
            "Invalid webhook signature rejected",
            extra={
                "event_id": delivery_id,
                "event_type": event_type,
                "processing_status": "rejected",
            },
        )
        raise HTTPException(status_code=401, detail="Invalid GitHub webhook signature")

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        logger.warning(
            "Malformed webhook payload",
            extra={
                "event_id": delivery_id,
                "event_type": event_type,
                "processing_status": "malformed",
            },
        )
        raise HTTPException(status_code=400, detail="Malformed JSON payload") from exc

    if event_type != "pull_request":
        logger.info(
            "Ignoring unsupported GitHub event",
            extra={
                "event_id": delivery_id,
                "event_type": event_type,
                "processing_status": "ignored",
            },
        )
        return {
            "status": "ignored",
            "event_type": event_type,
            "message": "Unsupported event type; no action taken.",
        }

    try:
        parsed = PullRequestEventPayload.model_validate(payload)
    except Exception as exc:  # pragma: no cover - kept simple for invalid payload handling
        logger.warning(
            "Invalid pull_request payload",
            extra={
                "event_id": delivery_id,
                "event_type": event_type,
                "processing_status": "invalid",
            },
        )
        raise HTTPException(status_code=400, detail="Invalid pull_request payload") from exc

    action = parsed.action
    if action not in SUPPORTED_PR_ACTIONS:
        logger.info(
            "Ignoring unsupported pull_request action",
            extra={
                "event_id": delivery_id,
                "event_type": event_type,
                "processing_status": "ignored",
                "pr_number": (parsed.pull_request.number if parsed.pull_request else None),
            },
        )
        return {
            "status": "ignored",
            "event_type": event_type,
            "action": action,
            "message": "Unsupported pull_request action; no action taken.",
        }

    if delivery_id:
        with SessionLocal() as db:
            existing = db.query(GitHubDelivery).filter(GitHubDelivery.delivery_id == delivery_id).first()
            if existing:
                logger.info(
                    "Duplicate GitHub delivery prevented",
                    extra={
                        "event_id": delivery_id,
                        "event_type": event_type,
                        "processing_status": "duplicate",
                        "repository": parsed.repository.full_name if parsed.repository else None,
                    },
                )
                return {
                    "status": "duplicate",
                    "event_type": event_type,
                    "action": action,
                    "message": "This event was already processed.",
                }

            db.add(
                GitHubDelivery(
                    delivery_id=delivery_id,
                    event_type=event_type,
                    repository_name=(parsed.repository.full_name if parsed.repository else "unknown"),
                )
            )
            db.commit()

    repository = parsed.repository
    pull_request = parsed.pull_request

    logger.info(
        "Processed pull_request webhook",
        extra={
            "event_id": delivery_id,
            "repository": repository.full_name if repository else None,
            "pr_number": pull_request.number if pull_request else None,
            "event_type": event_type,
            "processing_status": "processed",
        },
    )

    return {
        "status": "accepted",
        "event_type": event_type,
        "action": action,
        "repository": repository.full_name if repository else None,
        "pr_number": pull_request.number if pull_request else None,
        "author": pull_request.user.login if pull_request and pull_request.user else None,
        "head_branch": (pull_request.head or {}).get("ref") if pull_request and pull_request.head else None,
        "base_branch": (pull_request.base or {}).get("ref") if pull_request and pull_request.base else None,
        "head_sha": (pull_request.head or {}).get("sha") if pull_request and pull_request.head else None,
    }
