"""
Pydantic schemas for LINE Messaging API CRUD operations.
Used for request/response validation and serialization.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# ==================== Credential Schemas ====================

class SocialCredentialBase(BaseModel):
    """Base schema for social media credentials."""
    platform: str = Field(default="line", description="Platform name (e.g., 'line')")
    channel_access_token: str = Field(..., description="LINE Channel Access Token")
    channel_secret: Optional[str] = Field(None, description="LINE Channel Secret")
    target_id: Optional[str] = Field(None, description="Default LINE User ID for testing")


class SocialCredentialCreate(SocialCredentialBase):
    """Schema for creating a new credential."""
    pass


class SocialCredentialResponse(SocialCredentialBase):
    """Schema for credential responses."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic V2 (was orm_mode in V1)


# ==================== Post Schemas ====================

class SocialPostBase(BaseModel):
    """Base schema for social media posts."""
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Message text content"
    )
    platform: str = Field(default="line", description="Platform identifier")


class SocialPostCreate(SocialPostBase):
    """Schema for creating a new post."""
    credential_id: int = Field(..., description="Credential ID to use for publishing")
    target_id: str = Field(
        ...,
        description="LINE User ID to send message to (format: U...)"
    )


class SocialPostUpdate(BaseModel):
    """Schema for updating an existing post."""
    content: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Updated message text"
    )


class SocialPostResponse(SocialPostBase):
    """Schema for post responses."""
    id: int
    credential_id: int
    line_message_id: Optional[str] = Field(None, description="LINE's returned message ID")
    line_published_at: Optional[datetime] = Field(None, description="When message was sent")
    line_status: str = Field(description="Status: draft, published, failed, deleted, updated")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ==================== User Schemas ====================

class UserProfile(BaseModel):
    """Schema for LINE user profile data."""
    line_user_id: str
    display_name: Optional[str] = None
    picture_url: Optional[str] = None
    status_message: Optional[str] = None
    language: str = "zh-TW"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
