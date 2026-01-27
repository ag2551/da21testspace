"""LinkedIn REST API adapter"""
import httpx
from typing import Optional
from app.adapters.base import BaseSocialAdapter
from app.config import get_settings

settings = get_settings()


class LinkedInAdapter(BaseSocialAdapter):
    """Implements BaseSocialAdapter for LinkedIn REST API"""

    def __init__(self):
        self.base_url = settings.linkedin_base_url
        self.api_version = settings.linkedin_api_version

    def _get_headers(self, token: str) -> dict:
        """Get required headers for LinkedIn API"""
        return {
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": self.api_version,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

    async def validate_credentials(self, token: str) -> bool:
        """Validate LinkedIn access token"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.linkedin.com/v2/userinfo",
                    headers={"Authorization": f"Bearer {token}"}
                )
                return response.status_code == 200
            except Exception:
                return False

    async def publish_post(
        self,
        token: str,
        content: str,
        image_url: Optional[str] = None,
        author_urn: Optional[str] = None
    ) -> dict:
        """
        Publish post to LinkedIn using /rest/posts endpoint

        For images, uses two-step upload:
        1. Initialize upload via /rest/images?action=initializeUpload
        2. Upload binary to provided URL
        3. Reference image URN in post
        """
        if not author_urn:
            return {"success": False, "post_id": None, "error": "author_urn required"}

        async with httpx.AsyncClient() as client:
            try:
                # Build post payload
                payload = {
                    "author": author_urn,
                    "commentary": content,
                    "visibility": "PUBLIC",
                    "distribution": {
                        "feedDistribution": "MAIN_FEED",
                        "targetEntities": [],
                        "thirdPartyDistributionChannels": []
                    },
                    "lifecycleState": "PUBLISHED",
                    "isReshareDisabledByAuthor": False
                }

                # Handle image upload if provided
                if image_url:
                    image_urn = await self._upload_image(client, token, image_url, author_urn)
                    if image_urn:
                        payload["content"] = {
                            "media": {
                                "id": image_urn
                            }
                        }

                # Publish post
                response = await client.post(
                    f"{self.base_url}/posts",
                    json=payload,
                    headers=self._get_headers(token)
                )

                if response.status_code == 201:
                    # Post ID is in x-restli-id header
                    post_id = response.headers.get("x-restli-id")
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
                        "error": error_data.get("message", "Unknown error")
                    }
            except Exception as e:
                return {
                    "success": False,
                    "post_id": None,
                    "error": str(e)
                }

    async def _upload_image(
        self,
        client: httpx.AsyncClient,
        token: str,
        image_url: str,
        owner_urn: str
    ) -> Optional[str]:
        """
        Two-step image upload process for LinkedIn

        Returns image URN on success, None on failure
        """
        try:
            # Step 1: Initialize upload
            init_response = await client.post(
                f"{self.base_url}/images?action=initializeUpload",
                json={
                    "initializeUploadRequest": {
                        "owner": owner_urn
                    }
                },
                headers=self._get_headers(token)
            )

            if init_response.status_code != 200:
                return None

            init_data = init_response.json()
            upload_url = init_data["value"]["uploadUrl"]
            image_urn = init_data["value"]["image"]

            # Step 2: Download image from URL
            image_response = await client.get(image_url)
            if image_response.status_code != 200:
                return None

            # Step 3: Upload binary data
            upload_response = await client.post(
                upload_url,
                content=image_response.content,
                headers={"Authorization": f"Bearer {token}"}
            )

            if upload_response.status_code in [200, 201]:
                return image_urn

            return None
        except Exception:
            return None

    async def delete_post(self, token: str, post_id: str) -> bool:
        """Delete a LinkedIn post"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{self.base_url}/posts/{post_id}",
                    headers=self._get_headers(token)
                )
                return response.status_code == 204
            except Exception:
                return False

    async def get_post_status(self, token: str, post_id: str) -> dict:
        """Get LinkedIn post status"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/posts/{post_id}",
                    headers=self._get_headers(token)
                )
                if response.status_code == 200:
                    return {
                        "exists": True,
                        "data": response.json()
                    }
                return {"exists": False, "data": None}
            except Exception:
                return {"exists": False, "data": None}
