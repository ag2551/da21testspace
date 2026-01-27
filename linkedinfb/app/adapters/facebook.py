"""Facebook Graph API adapter"""
import httpx
from typing import Optional
from app.adapters.base import BaseSocialAdapter
from app.config import get_settings

settings = get_settings()


class FacebookAdapter(BaseSocialAdapter):
    """Implements BaseSocialAdapter for Facebook Graph API v24.0"""

    def __init__(self):
        self.base_url = f"{settings.facebook_base_url}/{settings.facebook_api_version}"

    async def validate_credentials(self, token: str) -> bool:
        """Validate Facebook Page Access Token"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/me",
                    params={"access_token": token}
                )
                return response.status_code == 200
            except Exception:
                return False

    async def publish_post(
        self,
        token: str,
        content: str,
        image_url: Optional[str] = None,
        page_id: Optional[str] = None
    ) -> dict:
        """
        Publish post to Facebook

        Uses /{page-id}/feed for text posts
        Uses /{page-id}/photos for posts with images
        """
        if not page_id:
            return {"success": False, "post_id": None, "error": "page_id required"}

        async with httpx.AsyncClient() as client:
            try:
                if image_url:
                    # POST to /photos endpoint for image posts
                    endpoint = f"{self.base_url}/{page_id}/photos"
                    data = {
                        "url": image_url,
                        "message": content,
                        "access_token": token
                    }
                else:
                    # POST to /feed endpoint for text posts
                    endpoint = f"{self.base_url}/{page_id}/feed"
                    data = {
                        "message": content,
                        "access_token": token
                    }

                response = await client.post(endpoint, data=data)

                if response.status_code in [200, 201]:
                    result = response.json()
                    post_id = result.get("post_id") or result.get("id")
                    return {
                        "success": True,
                        "post_id": post_id,
                        "error": None
                    }
                else:
                    error_data = response.json()
                    return {
                        "success": False,
                        "post_id": None,
                        "error": error_data.get("error", {}).get("message", "Unknown error")
                    }
            except Exception as e:
                return {
                    "success": False,
                    "post_id": None,
                    "error": str(e)
                }

    async def delete_post(self, token: str, post_id: str) -> bool:
        """Delete a Facebook post"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{self.base_url}/{post_id}",
                    params={"access_token": token}
                )
                return response.status_code == 200
            except Exception:
                return False

    async def get_post_status(self, token: str, post_id: str) -> dict:
        """Get Facebook post status"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/{post_id}",
                    params={
                        "access_token": token,
                        "fields": "id,message,created_time"
                    }
                )
                if response.status_code == 200:
                    return {
                        "exists": True,
                        "data": response.json()
                    }
                return {"exists": False, "data": None}
            except Exception:
                return {"exists": False, "data": None}
