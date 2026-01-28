"""Publishing orchestration service"""
from datetime import datetime
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.post import SocialPost
from app.models.credential import SocialCredential
from app.adapters.facebook import FacebookAdapter
from app.adapters.linkedin import LinkedInAdapter
from app.services.encryption import EncryptionService
from app.config import get_settings

settings = get_settings()


class PublisherService:
    """Orchestrates publishing to multiple platforms"""

    def __init__(self, session: AsyncSession, encryption_service: EncryptionService):
        self.session = session
        self.encryption = encryption_service
        self.facebook_adapter = FacebookAdapter()
        self.linkedin_adapter = LinkedInAdapter()

    async def publish_post(
        self,
        post_id: int,
        platforms: List[str]
    ) -> dict:
        """
        Publish a post to specified platforms

        Returns aggregated results for all platforms
        """
        # Get post
        result = await self.session.execute(
            select(SocialPost).where(SocialPost.id == post_id)
        )
        post = result.scalar_one_or_none()

        if not post:
            return {"error": "Post not found"}

        results = {}

        # Publish to each platform
        if "facebook" in platforms:
            fb_result = await self._publish_to_facebook(post)
            results["facebook"] = fb_result

            # Update post with Facebook results
            post.facebook_status = "success" if fb_result["success"] else "failed"
            post.facebook_post_id = fb_result.get("post_id")
            post.facebook_published_at = datetime.utcnow() if fb_result["success"] else None
            post.facebook_error = fb_result.get("error")

        if "linkedin" in platforms:
            li_result = await self._publish_to_linkedin(post)
            results["linkedin"] = li_result

            # Update post with LinkedIn results
            post.linkedin_status = "success" if li_result["success"] else "failed"
            post.linkedin_post_id = li_result.get("post_id")
            post.linkedin_published_at = datetime.utcnow() if li_result["success"] else None
            post.linkedin_error = li_result.get("error")

        # Update overall post status
        all_success = all(r.get("success") for r in results.values())
        post.status = "published" if all_success else "failed"
        post.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(post)

        return {
            "id": post.id,
            "status": post.status,
            "results": results
        }

    async def _publish_to_facebook(self, post: SocialPost) -> dict:
        """Publish to Facebook"""
        # Get active Facebook credential
        result = await self.session.execute(
            select(SocialCredential).where(
                SocialCredential.platform == "facebook",
                SocialCredential.is_active == True
            )
        )
        credential = result.first()

        if not credential:
            return {
                "success": False,
                "post_id": None,
                "error": "No active Facebook credential found"
            }

        # Decrypt token
        token = self.encryption.decrypt(credential[0].encrypted_token)

        # Get page_id from credential or fallback to settings
        page_id = credential[0].page_id_or_urn or settings.fb_page_id
        if not page_id:
            return {
                "success": False,
                "post_id": None,
                "error": "Facebook page_id not configured (provide in credential or set fb_page_id in .env)"
            }

        # Publish via adapter
        return await self.facebook_adapter.publish_post(
            token=token,
            content=post.content_text,
            image_url=post.content_image_url,
            page_id=page_id
        )

    async def _publish_to_linkedin(self, post: SocialPost) -> dict:
        """Publish to LinkedIn"""
        # Get active LinkedIn credential
        result = await self.session.execute(
            select(SocialCredential).where(
                SocialCredential.platform == "linkedin",
                SocialCredential.is_active == True
            )
        )
        credential = result.first()

        if not credential:
            return {
                "success": False,
                "post_id": None,
                "error": "No active LinkedIn credential found"
            }

        # Decrypt token
        token = self.encryption.decrypt(credential[0].encrypted_token)

        # Get author_urn from credential or fallback to settings
        author_urn = credential[0].page_id_or_urn or settings.linkedin_organization_urn
        if not author_urn:
            return {
                "success": False,
                "post_id": None,
                "error": "LinkedIn author URN not configured (provide in credential or set linkedin_organization_urn in .env)"
            }

        # Publish via adapter
        return await self.linkedin_adapter.publish_post(
            token=token,
            content=post.content_text,
            image_url=post.content_image_url,
            author_urn=author_urn
        )
