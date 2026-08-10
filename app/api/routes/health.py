from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", summary="Health check")
def health() -> dict[str, str]:
    """Return the application health status.

    This endpoint is intentionally lightweight and should be used by load balancers,
    deployment checks, and local validation.
    """
    return {"status": "healthy"}
