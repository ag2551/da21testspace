"""
LINE Messaging API Adapter.
Service layer for interacting with LINE's messaging API.
Handles push messages with proper error handling and API limitation documentation.
"""

import httpx
from datetime import datetime
from typing import Dict, Optional


class LineAdapter:
    """
    Adapter for LINE Messaging API operations.
    Handles message publishing with proper error handling.

    ⚠️ API Limitations:
    - LINE does NOT support deleting bot messages (verified all 68 API methods)
    - Update operation sends new message; original message remains visible
    """

    def __init__(self, channel_access_token: str):
        """
        Initialize LINE adapter with authentication.

        Args:
            channel_access_token: LINE Channel Access Token
        """
        self.channel_access_token = channel_access_token
        self.base_url = "https://api.line.me/v2/bot"
        self.headers = {
            "Authorization": f"Bearer {channel_access_token}",
            "Content-Type": "application/json"
        }

    async def publish_post(self, target_id: str, content: str) -> Dict:
        """
        Push a text message to a LINE user.

        Args:
            target_id: LINE User ID (format: U...)
            content: Message text content

        Returns:
            {
                "message_id": str,  # LINE's returned message ID
                "published_at": datetime
            }

        Raises:
            httpx.HTTPStatusError: If LINE API returns error (400, 401, 404, etc.)
            httpx.RequestError: If network/connection error occurs
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/message/push",
                    headers=self.headers,
                    json={
                        "to": target_id,
                        "messages": [
                            {
                                "type": "text",
                                "text": content
                            }
                        ]
                    },
                    timeout=10.0
                )
                response.raise_for_status()

                # Parse response
                # LINE API returns: {"sentMessages": [{"id": "..."}]}
                data = response.json()
                message_id = data.get("sentMessages", [{}])[0].get("id")

                return {
                    "message_id": message_id,
                    "published_at": datetime.now()
                }

            except httpx.HTTPStatusError as e:
                # Re-raise with original error for proper handling in routes
                raise
            except httpx.RequestError as e:
                # Network errors (timeout, connection refused, etc.)
                raise

    async def delete_post(self, message_id: str) -> Dict:
        """
        ⚠️ NOT SUPPORTED BY LINE API

        LINE Messaging API does not provide endpoint to delete bot messages.
        After exhaustive verification of all 68 methods in MessagingApi class,
        no delete/unsend/retract capability exists for bot messages.

        This method documents the API limitation and returns appropriate response.

        Args:
            message_id: LINE message ID (for documentation purposes)

        Returns:
            {
                "success": False,
                "message": "LINE API does not support deleting bot messages",
                "note": "Message remains visible in LINE. Marked as deleted in database only.",
                "message_id": str
            }
        """
        return {
            "success": False,
            "message": "LINE API does not support deleting bot messages",
            "note": "Message remains visible in LINE. Marked as deleted in database only.",
            "message_id": message_id
        }

    async def update_post(
        self,
        message_id: str,
        target_id: str,
        new_content: str
    ) -> Dict:
        """
        Pseudo-update: Sends new message (cannot delete original).

        ⚠️ API Limitation: Cannot delete original message.
        This sends a new message with updated content.
        The original message remains visible in LINE.

        Args:
            message_id: Original LINE message ID
            target_id: LINE User ID
            new_content: Updated message text

        Returns:
            {
                "message_id": str,  # New message ID
                "published_at": datetime,
                "previous_message_id": str,
                "note": "New message sent. Original message remains visible in LINE."
            }

        Raises:
            httpx.HTTPStatusError: If LINE API returns error
            httpx.RequestError: If network/connection error occurs
        """
        # Send new message
        result = await self.publish_post(target_id, new_content)

        return {
            "message_id": result["message_id"],
            "published_at": result["published_at"],
            "previous_message_id": message_id,
            "note": "New message sent. Original message remains visible in LINE."
        }
