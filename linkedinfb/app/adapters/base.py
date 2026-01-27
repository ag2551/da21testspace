"""Base adapter interface for social media platforms"""
from abc import ABC, abstractmethod
from typing import Optional


class BaseSocialAdapter(ABC):
    """Abstract base class for social media platform adapters"""

    @abstractmethod
    async def validate_credentials(self, token: str) -> bool:
        """Validate platform credentials"""
        pass

    @abstractmethod
    async def publish_post(
        self,
        token: str,
        content: str,
        image_url: Optional[str] = None
    ) -> dict:
        """
        Publish a post to the platform

        Returns:
            dict: {
                "success": bool,
                "post_id": str | None,
                "error": str | None
            }
        """
        pass

    @abstractmethod
    async def delete_post(self, token: str, post_id: str) -> bool:
        """Delete a post from the platform"""
        pass

    @abstractmethod
    async def get_post_status(self, token: str, post_id: str) -> dict:
        """Get the current status of a published post"""
        pass
