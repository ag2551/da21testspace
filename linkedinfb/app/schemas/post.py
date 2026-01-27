"""Pydantic schemas for posts"""
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List


class PostBase(BaseModel):
    """Base post schema"""
    content_text: str = Field(..., min_length=1, max_length=3000)
    content_image_url: Optional[HttpUrl] = None


class PostCreate(PostBase):
    """Schema for creating a post"""
    pass


class PostUpdate(BaseModel):
    """Schema for updating a post"""
    content_text: Optional[str] = Field(None, min_length=1, max_length=3000)
    content_image_url: Optional[HttpUrl] = None


class PostPublic(PostBase):
    """Public post schema"""
    id: int
    status: str
    scheduled_at: Optional[datetime]
    facebook_post_id: Optional[str]
    facebook_published_at: Optional[datetime]
    facebook_status: Optional[str]
    linkedin_post_id: Optional[str]
    linkedin_published_at: Optional[datetime]
    linkedin_status: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PostPublish(BaseModel):
    """Schema for publishing a post"""
    platforms: List[str] = Field(default=["facebook", "linkedin"])


class PostSchedule(BaseModel):
    """Schema for scheduling a post"""
    scheduled_at: datetime
    platforms: List[str] = Field(default=["facebook", "linkedin"])


class PlatformStatus(BaseModel):
    """Schema for platform-specific status"""
    status: str
    post_id: Optional[str]
    published_at: Optional[datetime]
    error: Optional[str]


class PostStatusResponse(BaseModel):
    """Schema for post status response"""
    id: int
    overall_status: str
    platforms: dict[str, PlatformStatus]
