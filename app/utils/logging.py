import logging
from typing import Any


class JsonFormatter(logging.Formatter):
    """Format log records as JSON-like structured output for production debugging."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "event_id"):
            payload["event_id"] = record.event_id
        if hasattr(record, "repository"):
            payload["repository"] = record.repository
        if hasattr(record, "pr_number"):
            payload["pr_number"] = record.pr_number
        if hasattr(record, "event_type"):
            payload["event_type"] = record.event_type
        if hasattr(record, "processing_status"):
            payload["processing_status"] = record.processing_status
        if hasattr(record, "processing_time"):
            payload["processing_time"] = record.processing_time

        return str(payload)


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("pr_risk_agent")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger
