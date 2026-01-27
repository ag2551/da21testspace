"""Post management endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List, Optional
from datetime import datetime

from app.database import get_async_session
from app.models.post import SocialPost
from app.schemas.post import (
    PostCreate,
    PostUpdate,
    PostPublic,
    PostPublish,
    PostSchedule,
    PostStatusResponse,
    PlatformStatus
)
from app.services.publisher import PublisherService
from app.services.encryption import get_encryption_service, EncryptionService

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("/", response_model=PostPublic, status_code=201)
async def create_post(
    *,
    session: AsyncSession = Depends(get_async_session),
    post: PostCreate
):
    """Create new post (draft)"""
    db_post = SocialPost(
        content_text=post.content_text,
        content_image_url=str(post.content_image_url) if post.content_image_url else None,
        status="draft"
    )

    session.add(db_post)
    await session.commit()
    await session.refresh(db_post)

    return db_post


@router.get("/", response_model=List[PostPublic])
async def list_posts(
    *,
    session: AsyncSession = Depends(get_async_session),
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """List all posts with optional filtering"""
    query = select(SocialPost)

    if status:
        query = query.where(SocialPost.status == status)

    query = query.offset(offset).limit(limit)

    result = await session.execute(query)
    posts = result.scalars().all()

    return posts


@router.get("/{post_id}", response_model=PostPublic)
async def get_post(
    *,
    session: AsyncSession = Depends(get_async_session),
    post_id: int
):
    """Get specific post"""
    result = await session.execute(
        select(SocialPost).where(SocialPost.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return post


@router.put("/{post_id}", response_model=PostPublic)
async def update_post(
    *,
    session: AsyncSession = Depends(get_async_session),
    post_id: int,
    post_update: PostUpdate
):
    """Update post (draft only)"""
    result = await session.execute(
        select(SocialPost).where(SocialPost.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Only draft posts can be edited"
        )

    # Update fields
    if post_update.content_text:
        post.content_text = post_update.content_text

    if post_update.content_image_url is not None:
        post.content_image_url = str(post_update.content_image_url) if post_update.content_image_url else None

    post.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(post)

    return post


@router.delete("/{post_id}", status_code=204)
async def delete_post(
    *,
    session: AsyncSession = Depends(get_async_session),
    post_id: int
):
    """Delete post"""
    result = await session.execute(
        select(SocialPost).where(SocialPost.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await session.delete(post)
    await session.commit()

    return None


@router.post("/{post_id}/publish")
async def publish_post(
    *,
    session: AsyncSession = Depends(get_async_session),
    post_id: int,
    publish_request: PostPublish,
    encryption: EncryptionService = Depends(get_encryption_service)
):
    """Publish post immediately to specified platforms"""
    publisher = PublisherService(session, encryption)
    result = await publisher.publish_post(post_id, publish_request.platforms)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result


@router.post("/{post_id}/schedule", response_model=PostPublic)
async def schedule_post(
    *,
    session: AsyncSession = Depends(get_async_session),
    post_id: int,
    schedule_request: PostSchedule
):
    """Schedule post for future publication"""
    result = await session.execute(
        select(SocialPost).where(SocialPost.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if schedule_request.scheduled_at <= datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="Scheduled time must be in the future"
        )

    post.scheduled_at = schedule_request.scheduled_at
    post.status = "scheduled"
    post.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(post)

    return post


@router.get("/{post_id}/status", response_model=PostStatusResponse)
async def get_post_status(
    *,
    session: AsyncSession = Depends(get_async_session),
    post_id: int
):
    """Get publication status for all platforms"""
    result = await session.execute(
        select(SocialPost).where(SocialPost.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return PostStatusResponse(
        id=post.id,
        overall_status=post.status,
        platforms={
            "facebook": PlatformStatus(
                status=post.facebook_status or "not_published",
                post_id=post.facebook_post_id,
                published_at=post.facebook_published_at,
                error=post.facebook_error
            ),
            "linkedin": PlatformStatus(
                status=post.linkedin_status or "not_published",
                post_id=post.linkedin_post_id,
                published_at=post.linkedin_published_at,
                error=post.linkedin_error
            )
        }
    )
