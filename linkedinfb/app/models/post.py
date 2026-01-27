"""SocialPost model"""
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional


class SocialPost(SQLModel, table=True):
    """Stores social media post content and publication status"""

    __tablename__ = "social_posts"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Content
    content_text: str
    content_image_url: Optional[str] = None

    # Status
    status: str = Field(default="draft")  # draft, scheduled, published, failed
    scheduled_at: Optional[datetime] = None

    # Facebook
    facebook_post_id: Optional[str] = None
    facebook_published_at: Optional[datetime] = None
    facebook_status: Optional[str] = None  # success, failed, pending
    facebook_error: Optional[str] = None

    # LinkedIn
    linkedin_post_id: Optional[str] = None
    linkedin_published_at: Optional[datetime] = None
    linkedin_status: Optional[str] = None  # success, failed, pending
    linkedin_error: Optional[str] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
