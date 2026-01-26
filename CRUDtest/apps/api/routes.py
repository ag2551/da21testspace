from typing import Dict
from ninja import NinjaAPI

api = NinjaAPI(
    title="Social Media Hub API",
    version="1.0.0",
    description="Async REST API for cross-platform social media publishing",
    docs_url="/docs",
)


@api.get("/health", tags=["System"])
async def health_check(request) -> Dict[str, str]:
    """
    Health check endpoint to verify API is running.

    Returns:
        dict: Status information including version and message
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "message": "Social Media Hub API is running"
    }
