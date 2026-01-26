from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseProvider(ABC):
    """
    Abstract base class for social media platform providers.

    All platform adapters must implement these methods to ensure
    consistent interface across different platforms.
    """

    @abstractmethod
    async def create_post(
        self,
        content: str,
        media: Optional[bytes] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a new post on the platform.

        Args:
            content: Text content of the post
            media: Optional media file as bytes
            **kwargs: Platform-specific parameters

        Returns:
            dict: Response containing post_id and metadata

        Raises:
            PlatformAPIError: If the API request fails
        """
        pass

    @abstractmethod
    async def update_post(
        self,
        post_id: str,
        content: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Update an existing post on the platform.

        Args:
            post_id: Platform-specific post identifier
            content: Updated text content
            **kwargs: Platform-specific parameters

        Returns:
            dict: Response containing update status

        Raises:
            PlatformAPIError: If the API request fails
        """
        pass

    @abstractmethod
    async def delete_post(self, post_id: str) -> bool:
        """
        Delete a post from the platform.

        Args:
            post_id: Platform-specific post identifier

        Returns:
            bool: True if deletion was successful

        Raises:
            PlatformAPIError: If the API request fails
        """
        pass

    @abstractmethod
    async def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        Retrieve post details from the platform.

        Args:
            post_id: Platform-specific post identifier

        Returns:
            dict: Post metadata and content

        Raises:
            PlatformAPIError: If the API request fails
        """
        pass


class PlatformAPIError(Exception):
    """Exception raised when platform API requests fail."""

    def __init__(self, platform: str, message: str, status_code: int = None):
        self.platform = platform
        self.message = message
        self.status_code = status_code
        super().__init__(f"{platform} API Error: {message}")
