"""
Social Media Hub - Pydantic Schemas

This module defines Pydantic schemas for API serialization,
converting Wagtail Page objects to JSON responses.
"""

from ninja import Schema
from typing import Literal, Optional, List, Dict, Any
from datetime import datetime
from wagtail.models import Page
from wagtail.rich_text import expand_db_html
from django.utils.html import strip_tags


class BasePageSchema(Schema):
    """
    Base schema for all Wagtail pages.
    Provides common fields for all page types.
    """
    id: int
    title: str
    slug: str
    url: Optional[str] = None
    content_type: str

    @staticmethod
    def resolve_content_type(page: Page) -> str:
        """Get page type name for discriminator."""
        return page.specific_class._meta.model_name

    @staticmethod
    def resolve_url(page: Page) -> str:
        """Get full URL for page."""
        try:
            return page.full_url or page.get_url()
        except Exception:
            return ""


class SocialPostPageSchema(BasePageSchema):
    """
    Schema for SocialPostPage.
    Uses content_type as discriminator for polymorphic serialization.
    """
    content_type: Literal["socialpostpage"]

    # Post content (converted from StreamField)
    headline: str
    body_html: str  # Converted from RichTextBlock
    body_text: str  # Plain text version
    
    # Media
    image_url: Optional[str] = None

    # Publishing settings
    publish_to_facebook: bool
    publish_to_linkedin: bool
    publish_to_line: bool

    scheduled_publish_time: Optional[datetime] = None

    @staticmethod
    def resolve_headline(page) -> str:
        """Extract headline from StreamField."""
        try:
            for block in page.content:
                if block.block_type == 'post':
                    return block.value['headline']
        except Exception:
            pass
        return ""

    @staticmethod
    def resolve_body_html(page) -> str:
        """Convert RichTextBlock to HTML."""
        try:
            for block in page.content:
                if block.block_type == 'post':
                    return expand_db_html(block.value['body'])
        except Exception:
            pass
        return ""

    @staticmethod
    def resolve_body_text(page) -> str:
        """Convert RichTextBlock to plain text."""
        html = SocialPostPageSchema.resolve_body_html(page)
        return strip_tags(html)

    @staticmethod
    def resolve_image_url(page) -> Optional[str]:
        """Extract image URL from StreamField."""
        try:
            for block in page.content:
                if block.block_type == 'post':
                    image = block.value.get('image')
                    if image:
                        return image.file.url
        except Exception:
            pass
        return None


class PostStatusResponse(Schema):
    """Schema for post status API responses."""
    
    uuid: str
    status: str
    content: str
    platforms: List[str]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    
    # Platform-specific post IDs
    facebook_post_id: Optional[str] = None
    linkedin_post_id: Optional[str] = None
    line_message_id: Optional[str] = None
    
    # Platform URLs
    platform_urls: Dict[str, str] = {}
    
    # Error tracking
    retry_count: int
    last_error: Optional[str] = None


class PlatformRecordSchema(Schema):
    """Schema for individual platform publish records."""
    
    platform: str
    status: str
    platform_post_id: Optional[str] = None
    platform_url: Optional[str] = None
    
    published_at: Optional[datetime] = None
    
    # Error details
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    retry_count: int
    
    # Media tracking
    media_uploaded: bool
    media_asset_urn: Optional[str] = None


class PostDetailResponse(PostStatusResponse):
    """Extended schema with platform records."""
    
    platform_records: List[PlatformRecordSchema] = []
    
    # Wagtail integration
    wagtail_page_id: Optional[int] = None
    streamfield_data: Dict[str, Any] = {}


class PublishRequestSchema(Schema):
    """Schema for publish request."""
    
    content: str
    platforms: List[str]
    
    # Optional fields
    scheduled_for: Optional[datetime] = None
    wagtail_page_id: Optional[int] = None


class CredentialSchema(Schema):
    """Schema for social credentials (without sensitive data)."""
    
    id: int
    platform: str
    account_name: str
    
    # Platform identifiers (non-sensitive)
    facebook_page_id: Optional[str] = None
    linkedin_org_urn: Optional[str] = None
    line_channel_id: Optional[str] = None
    
    # Status
    is_active: bool
    token_expires_at: Optional[datetime] = None
    is_token_expiring_soon: bool
    last_verified_at: Optional[datetime] = None
    
    created_at: datetime
    updated_at: datetime


class LineAudienceSchema(Schema):
    """Schema for LINE audience members."""
    
    id: int
    line_user_id: str
    display_name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    
    tags: List[str] = []
    
    # Interaction history
    first_interaction: datetime
    last_interaction: datetime
    message_count: int
    
    # Status
    is_active: bool
    is_blocked: bool
    opted_out_at: Optional[datetime] = None


class HealthCheckResponse(Schema):
    """Schema for health check endpoint."""
    
    status: str
    version: str
    message: str
    timestamp: datetime = datetime.now()


class ErrorResponse(Schema):
    """Schema for error responses."""
    
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
