from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.webhooks import router as webhook_router
from app.config import settings

app = FastAPI(
    title="PR Risk Agent",
    version=settings.app_version,
    description="GitHub-integrated backend for analyzing pull request risk.",
)

app.include_router(health_router)
app.include_router(webhook_router)


@app.get("/")
def read_root() -> dict[str, str]:
    """Return a simple app-level status message."""
    return {"app": settings.app_name, "status": "running"}
