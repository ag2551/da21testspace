"""LinkedIn REST API adapter"""
import httpx
import logging
from typing import Optional
from app.adapters.base import BaseSocialAdapter
from app.config import get_settings

logger = logging.getLogger(__name__)
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
        Publish post to LinkedIn using /rest/posts endpoint (Community Management API)
        
        Note: For MVP, images are handled by appending URL to text rather than binary upload.
        """
        if not author_urn:
            return {"success": False, "post_id": None, "error": "author_urn required"}

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Step 1: Verify token and get actual user info
                logger.info("Verifying LinkedIn token...")
                userinfo_response = await client.get(
                    "https://api.linkedin.com/v2/userinfo",
                    headers={"Authorization": f"Bearer {token}"}
                )
                
                if userinfo_response.status_code != 200:
                    error_msg = f"Token validation failed (HTTP {userinfo_response.status_code}): {userinfo_response.text[:200]}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "post_id": None,
                        "error": error_msg
                    }
                
                user_info = userinfo_response.json()
                actual_person_id = user_info.get("sub")
                logger.info(f"Token validated. User sub: {actual_person_id}, User name: {user_info.get('name')}")
                
                # Construct correct URN from token owner
                correct_author_urn = f"urn:li:person:{actual_person_id}"
                
                # Warn if provided URN doesn't match
                if author_urn != correct_author_urn:
                    logger.warning(f"Author URN mismatch! Provided: {author_urn}, Correct: {correct_author_urn}")
                    logger.info(f"Using correct URN from token: {correct_author_urn}")
                    author_urn = correct_author_urn

                # Build commentary text - append image URL if provided (MVP approach)
                commentary_text = content
                if image_url:
                    commentary_text = f"{content}\n\n🖼️ Image: {image_url}"
                    logger.info(f"Image URL appended to commentary: {image_url}")

                # Build post payload for new LinkedIn REST API
                payload = {
                    "author": author_urn,
                    "commentary": commentary_text,
                    "visibility": "PUBLIC",
                    "distribution": {
                        "feedDistribution": "MAIN_FEED",
                        "targetEntities": [],
                        "thirdPartyDistributionChannels": []
                    },
                    "lifecycleState": "PUBLISHED",
                    "isReshareDisabledByAuthor": False
                }

                headers = self._get_headers(token)

                # Log request details for debugging
                logger.info(f"Publishing post to LinkedIn: {self.base_url}/posts")
                logger.info(f"Using LinkedIn API version: {self.api_version}")
                logger.info(f"Author URN: {author_urn}")
                logger.info(f"Headers: {', '.join([f'{k}: {v[:20]}...' if k == 'Authorization' else f'{k}: {v}' for k, v in headers.items()])}")
                logger.info(f"Payload keys: {list(payload.keys())}")
                
                response = await client.post(
                    f"{self.base_url}/posts",
                    json=payload,
                    headers=headers
                )
                
                logger.info(f"LinkedIn API response status: {response.status_code}")
                logger.info(f"Response headers: {dict(response.headers)}")

                if response.status_code == 201:
                    # Post ID is in x-restli-id header
                    post_id = response.headers.get("x-restli-id")
                    logger.info(f"LinkedIn post published successfully: {post_id}")
                    return {
                        "success": True,
                        "post_id": post_id,
                        "error": None
                    }
                else:
                    # Log full response for debugging
                    logger.error(f"Full response body: {response.text}")
                    
                    # Try to parse error response
                    try:
                        error_data = response.json()
                        logger.error(f"LinkedIn API error response: {error_data}")
                        
                        # Extract error message from various possible fields
                        error_message = (
                            error_data.get("message") or 
                            error_data.get("error") or 
                            error_data.get("error_description") or
                            f"HTTP {response.status_code}"
                        )
                        
                        # If serviceErrorCode exists, include it
                        if "serviceErrorCode" in error_data:
                            error_message = f"LinkedIn Error {error_data['serviceErrorCode']}: {error_message}"
                    except:
                        error_message = f"HTTP {response.status_code}: {response.text[:300]}"
                    
                    logger.error(f"LinkedIn publish failed: {error_message}")
                    return {
                        "success": False,
                        "post_id": None,
                        "error": error_message
                    }
            except httpx.TimeoutException as e:
                error_msg = f"Timeout: LinkedIn API request timed out"
                logger.error(error_msg, exc_info=True)
                return {
                    "success": False,
                    "post_id": None,
                    "error": error_msg
                }
            except httpx.RequestError as e:
                error_msg = f"Network error: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return {
                    "success": False,
                    "post_id": None,
                    "error": error_msg
                }
            except Exception as e:
                error_msg = f"Unexpected error: {type(e).__name__}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return {
                    "success": False,
                    "post_id": None,
                    "error": error_msg
                }

    async def _upload_image(
        self,
        client: httpx.AsyncClient,
        token: str,
        image_url: str,
        owner_urn: str
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Two-step image upload process for LinkedIn

        Returns (image_urn, error_message) tuple
        """
        try:
            # Step 1: Initialize upload
            logger.info(f"Initializing LinkedIn image upload")
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
                error_msg = f"Image init failed (HTTP {init_response.status_code}): {init_response.text[:200]}"
                logger.error(error_msg)
                return None, error_msg

            init_data = init_response.json()
            upload_url = init_data["value"]["uploadUrl"]
            image_urn = init_data["value"]["image"]
            logger.info(f"Image upload initialized: {image_urn}")

            # Step 2: Download image from URL
            logger.info(f"Downloading image from: {image_url}")
            image_response = await client.get(image_url, timeout=30.0)
            if image_response.status_code != 200:
                error_msg = f"Image download failed (HTTP {image_response.status_code})"
                logger.error(error_msg)
                return None, error_msg

            logger.info(f"Image downloaded: {len(image_response.content)} bytes")

            # Step 3: Upload binary data
            logger.info(f"Uploading image binary to LinkedIn")
            upload_response = await client.post(
                upload_url,
                content=image_response.content,
                headers={"Authorization": f"Bearer {token}"}
            )

            if upload_response.status_code in [200, 201]:
                logger.info(f"Image binary uploaded successfully")
                return image_urn, None
            else:
                error_msg = f"Image binary upload failed (HTTP {upload_response.status_code}): {upload_response.text[:200]}"
                logger.error(error_msg)
                return None, error_msg

        except Exception as e:
            error_msg = f"Image upload exception: {type(e).__name__}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return None, error_msg

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
