# Lightweight Social Media Hub - Project Specification

## Overview

A lightweight social media management platform for publishing content to multiple social networks. This MVP focuses on Facebook and LinkedIn integration with CRUD operations and scheduled publishing capabilities.

## Technology Stack

### Core Framework
- **FastAPI** - Modern, high-performance web framework for building APIs
- **SQLModel** - Combined SQLAlchemy ORM + Pydantic validation
- **SQLite** - Single-file embedded database for simplicity
- **HTTPX** - Async HTTP client for external API calls

### Additional Dependencies
- **SQLAlchemy[asyncio]** - For async database operations with SQLModel
- **Aiosqlite** - Async driver for SQLite database
- **Cryptography** - For encrypting platform tokens
- **Python-Multipart** - For handling file uploads (images)
- **Uvicorn** - ASGI server for running FastAPI

## Architecture

### Project Structure

```
social-media-hub/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration settings
│   ├── database.py             # SQLModel database setup
│   ├── models/
│   │   ├── __init__.py
│   │   ├── credential.py       # SocialCredential model
│   │   └── post.py             # SocialPost model
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py             # Base adapter interface
│   │   ├── facebook.py         # Facebook adapter implementation
│   │   └── linkedin.py         # LinkedIn adapter implementation
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── credentials.py      # Credential management endpoints
│   │   └── posts.py            # Post management endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── encryption.py       # Token encryption service
│   │   └── publisher.py        # Publishing orchestration service
│   └── schemas/
│       ├── __init__.py
│       ├── credential.py       # Pydantic schemas for credentials
│       └── post.py             # Pydantic schemas for posts
├── tests/
│   ├── __init__.py
│   ├── test_adapters.py
│   ├── test_posts.py
│   └── test_credentials.py
├── data/
│   └── social_hub.db           # SQLite database file
├── requirements.txt
├── .env.example
└── README.md
```

## Data Models

### SocialCredential

Stores encrypted authentication tokens for each platform.

```python
class SocialCredential(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    platform: str = Field(index=True)  # "facebook" or "linkedin"
    account_name: str                   # Friendly name for the account
    encrypted_token: str                # Encrypted access token
    token_expires_at: datetime | None   # Token expiration time
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
```

### SocialPost

Stores post content and publication status across platforms.

```python
class SocialPost(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content_text: str                   # Post text content
    content_image_url: str | None       # Optional image URL/path

    # Publication status
    status: str = Field(default="draft")  # "draft", "scheduled", "published", "failed"
    scheduled_at: datetime | None       # When to publish (if scheduled)

    # Platform-specific post IDs (for tracking published posts)
    facebook_post_id: str | None
    facebook_published_at: datetime | None
    facebook_status: str | None         # "success", "failed", "pending"
    facebook_error: str | None

    linkedin_post_id: str | None
    linkedin_published_at: datetime | None
    linkedin_status: str | None         # "success", "failed", "pending"
    linkedin_error: str | None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

## Adapter Pattern

### Base Adapter Interface

All platform adapters must implement this interface:

```python
class BaseSocialAdapter(ABC):
    """Abstract base class for social media platform adapters"""

    @abstractmethod
    async def validate_credentials(self, token: str) -> bool:
        """Validate platform credentials"""
        pass

    @abstractmethod
    async def publish_post(self, token: str, content: str, image_url: str | None) -> dict:
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
```

### Platform Implementations

- **`adapters/facebook.py`**: Implements BaseSocialAdapter for Facebook Graph API v24.0
  - Uses `/{page-id}/feed` for text posts
  - Uses `/{page-id}/photos` for image posts
  - Supports both URL-based and binary file uploads
- **`adapters/linkedin.py`**: Implements BaseSocialAdapter for LinkedIn REST API
  - Uses `/rest/posts` endpoint (migrated from deprecated `/v2/ugcPosts`)
  - Implements two-step image upload via `/rest/images?action=initializeUpload`
  - Handles new simplified payload format with direct `commentary` field

## API Endpoints

### Credentials Management

```
POST   /api/credentials              # Create new platform credential
GET    /api/credentials              # List all credentials
GET    /api/credentials/{id}         # Get specific credential
PUT    /api/credentials/{id}         # Update credential
DELETE /api/credentials/{id}         # Delete credential
POST   /api/credentials/{id}/validate # Validate credential with platform
```

### Posts Management

```
POST   /api/posts                    # Create new post (draft)
GET    /api/posts                    # List all posts (with filtering)
GET    /api/posts/{id}               # Get specific post
PUT    /api/posts/{id}               # Update post
DELETE /api/posts/{id}               # Delete post
POST   /api/posts/{id}/publish       # Trigger immediate publication
POST   /api/posts/{id}/schedule      # Schedule post for future publication
GET    /api/posts/{id}/status        # Get publication status for all platforms
```

## Core Features

### 1. Credential Management
- Store platform access tokens securely (encrypted at rest)
- Support multiple accounts per platform
- Validate credentials before saving
- Token expiration tracking

### 2. Post Management
- Create posts with text content
- Optional image attachment
- Draft state before publication
- Edit posts before publishing

### 3. Publication
- Immediate publication to selected platforms
- Schedule posts for future publication
- Track publication status per platform
- Store platform-specific post IDs for reference
- Error handling and retry logic

### 4. Status Tracking
- Per-platform publication status
- Error messages for failed publications
- Timestamp tracking for all publications

## Security Considerations

### Token Encryption
- Use `cryptography.fernet` for symmetric encryption
- Store encryption key in environment variable
- Never expose decrypted tokens in API responses

### Token Storage
```python
# Encryption key stored in .env
ENCRYPTION_KEY=<base64-encoded-key>

# Tokens encrypted before database storage
encrypted_token = encrypt(access_token, ENCRYPTION_KEY)
```

## MVP Limitations

### What's Included
- Facebook and LinkedIn only
- Text posts with optional single image
- Manual credential input (access tokens)
- Basic CRUD operations
- Single-user system (no authentication)

### What's NOT Included (Future Enhancements)
- Twitter/X, Instagram, TikTok, etc.
- OAuth2 flows for token acquisition
- Multi-user support with authentication
- Post analytics and engagement metrics
- Post scheduling with background workers
- Video content support
- Hashtag suggestions
- Post templates
- Content calendar view
- Bulk operations

## Environment Configuration

```env
# .env file
DATABASE_URL=sqlite+aiosqlite:///./data/social_hub.db
ENCRYPTION_KEY=<generated-fernet-key>
DEBUG=true

# Facebook API (optional for testing)
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=

# LinkedIn API (optional for testing)
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
```

## External API Integration

### Facebook Graph API
- **Base Endpoint**: `https://graph.facebook.com/v24.0/`
- **Authentication**: Access Token (Page Access Token)
- **Publish Endpoints**:
  - Text posts: `POST /{page-id}/feed` with `message` parameter
  - Photo posts: `POST /{page-id}/photos` with `url` or `source` parameter
- **Required Permissions**: `pages_manage_posts`, `pages_read_engagement`
- **Note**: Use Page Access Token (not User Access Token) obtained via `GET /me/accounts`

### LinkedIn API (REST)
- **Base Endpoint**: `https://api.linkedin.com/rest/`
- **Authentication**: OAuth 2.0 Access Token (Bearer)
- **Publish Endpoints**:
  - Text posts: `POST /posts` with simplified JSON payload
  - Image upload: Two-step process via `POST /images?action=initializeUpload`
- **Required Headers**:
  - `Authorization: Bearer {ACCESS_TOKEN}`
  - `LinkedIn-Version: {YYYYMM}` (e.g., 202601)
  - `X-Restli-Protocol-Version: 2.0.0`
  - `Content-Type: application/json`
- **Required Permissions**: `w_member_social` or `w_organization_social`
- **Note**: Migrated from deprecated `/v2/ugcPosts` endpoint. New payload format uses direct `commentary` field instead of nested `specificContent.shareCommentary.text`

## Async Database Configuration

### Database Setup (database.py)

Since we're using **HTTPX** for async HTTP calls to external APIs, all database operations should also be async to avoid blocking:

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel

# Use aiosqlite driver for async SQLite
DATABASE_URL = "sqlite+aiosqlite:///./data/social_hub.db"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevents detached instance errors
)

# Database initialization
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

# Dependency for FastAPI endpoints
async def get_async_session():
    async with async_session_maker() as session:
        yield session
```

### Usage in FastAPI Endpoints

```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

@app.post("/api/posts/", response_model=SocialPostPublic)
async def create_post(
    *,
    session: AsyncSession = Depends(get_async_session),
    post: SocialPostCreate
):
    db_post = SocialPost.model_validate(post)
    session.add(db_post)
    await session.commit()  # Non-blocking
    await session.refresh(db_post)
    return db_post

@app.post("/api/posts/{id}/publish")
async def publish_post(
    *,
    session: AsyncSession = Depends(get_async_session),
    post_id: int
):
    # Database query (async)
    result = await session.execute(
        select(SocialPost).where(SocialPost.id == post_id)
    )
    post = result.scalar_one_or_none()

    # External API calls (async with HTTPX)
    async with httpx.AsyncClient() as client:
        response = await client.post(...)

    # Update database (async)
    post.status = "published"
    await session.commit()

    return post
```

### Key Points

- ⚠️ **SQLModel doesn't have native async wrappers** - Use SQLAlchemy's `AsyncSession` directly
- ✅ All session operations require `await`: `commit()`, `refresh()`, `execute()`
- ✅ Use `aiosqlite` driver with connection string: `sqlite+aiosqlite:///path/to/db.db`
- ✅ Set `expire_on_commit=False` to avoid detached instance issues
- ✅ Async database operations pair perfectly with async HTTP calls (HTTPX)

## Development Workflow

### Phase 1: Foundation (Week 1)
1. Set up FastAPI project structure
2. Implement SQLModel models
3. Create database initialization
4. Implement encryption service

### Phase 2: Adapters (Week 1-2)
1. Implement base adapter interface
2. Create Facebook adapter
3. Create LinkedIn adapter
4. Write adapter tests

### Phase 3: API Endpoints (Week 2)
1. Implement credential endpoints
2. Implement post endpoints
3. Create publisher service
4. Add validation and error handling

### Phase 4: Testing & Documentation (Week 2-3)
1. Integration tests
2. API documentation (FastAPI automatic docs)
3. README with setup instructions
4. Example usage scripts

## Success Criteria

- [ ] Store and encrypt credentials for Facebook and LinkedIn
- [ ] Create, read, update, delete posts
- [ ] Publish text posts to both platforms
- [ ] Publish posts with images to both platforms
- [ ] Track publication status per platform
- [ ] Handle API errors gracefully
- [ ] Store platform post IDs for reference
- [ ] Provide clear API documentation

## Open Questions

1. **Image Storage**: Should images be stored locally or use external URLs only?
2. **Scheduling**: Use background worker (Celery) or simple cron job for scheduled posts?
3. **Validation**: Should we validate post content length limits per platform?
4. **Retry Logic**: How many retry attempts for failed publications?

---

## Recent Updates (2026-01-27)

### ✅ Research-Based Technical Updates

Based on comprehensive technical research of latest API standards:

1. **LinkedIn API Migration**
   - ✅ Updated from deprecated `/v2/ugcPosts` to `/rest/posts`
   - ✅ New simplified payload format (direct `commentary` field)
   - ✅ Two-step image upload via `/rest/images?action=initializeUpload`
   - ✅ Required headers documented: `LinkedIn-Version`, `X-Restli-Protocol-Version`

2. **Facebook Graph API Clarification**
   - ✅ Updated to v24.0
   - ✅ Separated endpoints: `/{page-id}/feed` for text, `/{page-id}/photos` for images
   - ✅ Documented Page Access Token requirement

3. **Async Database Architecture**
   - ✅ Added SQLAlchemy[asyncio] and aiosqlite dependencies
   - ✅ Updated DATABASE_URL to `sqlite+aiosqlite://` format
   - ✅ Comprehensive async patterns documentation
   - ✅ AsyncSession usage examples with FastAPI

---

**Version**: 1.1
**Date**: 2026-01-27
**Status**: Updated - Ready for Implementation
