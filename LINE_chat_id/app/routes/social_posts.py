"""
CRUD API routes for LINE social posts.
All database operations use native SQL with parameterized queries.
"""

from fastapi import APIRouter, Depends, HTTPException
import aiosqlite
from datetime import datetime
from typing import List

from app.database import get_db_connection
from app.schemas import (
    SocialPostCreate,
    SocialPostUpdate,
    SocialPostResponse,
    SocialCredentialCreate,
    SocialCredentialResponse
)
from app.line_adapter import LineAdapter


# Create router for social posts endpoints
router = APIRouter(prefix="/api", tags=["Social Posts"])


# ==================== Credential Endpoints ====================

@router.post("/credentials", response_model=SocialCredentialResponse, status_code=201)
async def create_credential(
    credential: SocialCredentialCreate,
    db: aiosqlite.Connection = Depends(get_db_connection)
):
    """
    Create a new social media credential.
    Used to store LINE Channel Access Token for API authentication.
    """
    cursor = await db.execute(
        """
        INSERT INTO social_credentials (platform, channel_access_token, channel_secret, target_id)
        VALUES (?, ?, ?, ?)
        """,
        (credential.platform, credential.channel_access_token, credential.channel_secret, credential.target_id)
    )
    await db.commit()
    credential_id = cursor.lastrowid

    # Return created credential
    cursor = await db.execute(
        "SELECT * FROM social_credentials WHERE id = ?",
        (credential_id,)
    )
    row = await cursor.fetchone()
    return dict(row)


@router.get("/credentials/{credential_id}", response_model=SocialCredentialResponse)
async def get_credential(
    credential_id: int,
    db: aiosqlite.Connection = Depends(get_db_connection)
):
    """Retrieve a specific credential by ID."""
    cursor = await db.execute(
        "SELECT * FROM social_credentials WHERE id = ?",
        (credential_id,)
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Credential not found")
    return dict(row)


# ==================== Post CRUD Endpoints ====================

@router.post("/posts", response_model=SocialPostResponse, status_code=201)
async def create_post(
    post: SocialPostCreate,
    db: aiosqlite.Connection = Depends(get_db_connection)
):
    """
    Create and publish a LINE message.

    Flow:
    1. INSERT post as 'draft' status
    2. Call LINE API to push message
    3. UPDATE post with message_id and 'published' status

    Errors:
    - 404: Credential not found
    - 500: LINE API error (invalid token, user not found, etc.)
    """
    # Get credential
    cursor = await db.execute(
        "SELECT channel_access_token FROM social_credentials WHERE id = ?",
        (post.credential_id,)
    )
    credential = await cursor.fetchone()
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    # Insert post as draft
    cursor = await db.execute(
        """
        INSERT INTO social_posts (platform, content, credential_id, line_status)
        VALUES (?, ?, ?, ?)
        """,
        (post.platform, post.content, post.credential_id, "draft")
    )
    await db.commit()
    post_id = cursor.lastrowid

    # Publish to LINE
    adapter = LineAdapter(credential["channel_access_token"])
    try:
        result = await adapter.publish_post(post.target_id, post.content)

        # Update with LINE message ID
        await db.execute(
            """
            UPDATE social_posts
            SET line_message_id = ?,
                line_published_at = ?,
                line_status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (result["message_id"], result["published_at"], "published", post_id)
        )
        await db.commit()

    except Exception as e:
        # Mark as failed
        await db.execute(
            "UPDATE social_posts SET line_status = ? WHERE id = ?",
            ("failed", post_id)
        )
        await db.commit()
        raise HTTPException(status_code=500, detail=f"LINE API error: {str(e)}")

    # Return created post
    cursor = await db.execute("SELECT * FROM social_posts WHERE id = ?", (post_id,))
    row = await cursor.fetchone()
    return dict(row)


@router.get("/posts/{post_id}", response_model=SocialPostResponse)
async def get_post(
    post_id: int,
    db: aiosqlite.Connection = Depends(get_db_connection)
):
    """
    Read a single post from database.
    No LINE API call needed - returns database record only.
    """
    cursor = await db.execute(
        "SELECT * FROM social_posts WHERE id = ?",
        (post_id,)
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")
    return dict(row)


@router.get("/posts", response_model=List[SocialPostResponse])
async def list_posts(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    db: aiosqlite.Connection = Depends(get_db_connection)
):
    """
    List all posts with optional filtering.

    Query params:
    - skip: Offset for pagination (default: 0)
    - limit: Max results per page (default: 20, max: 100)
    - status: Filter by line_status (draft, published, failed, deleted, updated)
    """
    if limit > 100:
        limit = 100

    query = "SELECT * FROM social_posts"
    params = []

    if status:
        query += " WHERE line_status = ?"
        params.append(status)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, skip])

    cursor = await db.execute(query, tuple(params))
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


@router.put("/posts/{post_id}", response_model=SocialPostResponse)
async def update_post(
    post_id: int,
    post_update: SocialPostUpdate,
    db: aiosqlite.Connection = Depends(get_db_connection)
):
    """
    Update post by sending new LINE message.

    ⚠️ API Limitation: Original message remains visible in LINE.
    This sends a new message with updated content and stores the new message_id.

    Errors:
    - 404: Post not found
    - 500: LINE API error
    """
    # Get existing post with credential
    cursor = await db.execute(
        """
        SELECT sp.*, sc.channel_access_token, sc.target_id
        FROM social_posts sp
        JOIN social_credentials sc ON sp.credential_id = sc.id
        WHERE sp.id = ?
        """,
        (post_id,)
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")

    post_data = dict(row)

    # Send new message
    adapter = LineAdapter(post_data["channel_access_token"])
    try:
        result = await adapter.update_post(
            post_data["line_message_id"],
            post_data["target_id"],
            post_update.content
        )

        # Update database
        await db.execute(
            """
            UPDATE social_posts
            SET content = ?,
                line_message_id = ?,
                line_published_at = ?,
                line_status = 'updated',
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (post_update.content, result["message_id"], result["published_at"], post_id)
        )
        await db.commit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")

    # Return updated post
    cursor = await db.execute("SELECT * FROM social_posts WHERE id = ?", (post_id,))
    row = await cursor.fetchone()
    return dict(row)


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: int,
    db: aiosqlite.Connection = Depends(get_db_connection)
):
    """
    Soft delete post in database.

    ⚠️ API Limitation: Message remains visible in LINE.
    LINE Messaging API does not support deleting bot messages.
    This endpoint marks the message as 'deleted' in database only.

    Errors:
    - 404: Post not found
    """
    # Check if post exists
    cursor = await db.execute(
        "SELECT id FROM social_posts WHERE id = ?",
        (post_id,)
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")

    # Soft delete
    await db.execute(
        """
        UPDATE social_posts
        SET line_status = 'deleted', updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (post_id,)
    )
    await db.commit()

    return {
        "success": True,
        "message": "Post marked as deleted in database",
        "note": "Message remains visible in LINE. LINE Messaging API does not support deleting bot messages.",
        "post_id": post_id
    }
