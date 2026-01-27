# Product Requirement Document (PRD)
# Lightweight Social Media Hub

**Version**: 1.0
**Date**: 2026-01-27
**Status**: Ready for Review
**Source**: INITIAL.md v1.1

---

## 1. Executive Summary

### 1.1 Product Vision
Build a lightweight, developer-friendly social media management platform that enables seamless content publishing to multiple social networks (Facebook and LinkedIn) through a unified API interface.

### 1.2 Product Goals
- Provide a simple REST API for managing social media posts across platforms
- Secure credential storage with encryption at rest
- Track publication status independently for each platform
- Support both text and image content
- Enable scheduled publishing for future content planning

### 1.3 Target Users
- **Primary**: Small businesses, content creators, and developers who need programmatic social media posting
- **Secondary**: Marketing teams looking for a lightweight alternative to enterprise tools
- **Use Case**: API-first approach for integration into existing workflows and automation scripts

### 1.4 Success Metrics
- Successfully publish posts to Facebook and LinkedIn
- Securely store and manage platform credentials
- Track publication status with <5% failure rate
- Sub-second API response times for CRUD operations
- Zero exposed sensitive credentials in logs or responses

---

## 2. User Stories

### 2.1 Epic 1: Credential Management

#### Story 1.1: Add Social Media Credentials
**As a** user
**I want to** securely store my Facebook and LinkedIn access tokens
**So that** the system can publish content on my behalf without exposing my credentials

**Acceptance Criteria**:
- [ ] User can submit access token via POST request
- [ ] Token is encrypted before database storage using Fernet encryption
- [ ] Token expiration timestamp is stored for tracking
- [ ] System validates token with platform API before saving
- [ ] Multiple accounts per platform are supported
- [ ] Response does not include decrypted token

**API Endpoint**: `POST /api/credentials`

**Request Example**:
```json
{
  "platform": "linkedin",
  "account_name": "My Company LinkedIn",
  "access_token": "AQV...",
  "token_expires_at": "2026-03-27T00:00:00Z"
}
```

**Response Example**:
```json
{
  "id": 1,
  "platform": "linkedin",
  "account_name": "My Company LinkedIn",
  "token_expires_at": "2026-03-27T00:00:00Z",
  "is_active": true,
  "created_at": "2026-01-27T18:00:00Z"
}
```

#### Story 1.2: List All Credentials
**As a** user
**I want to** view all my stored credentials
**So that** I can manage multiple social media accounts

**Acceptance Criteria**:
- [ ] User can retrieve list of all credentials
- [ ] Response includes platform, account name, and metadata
- [ ] Encrypted tokens are never returned in response
- [ ] Results show token expiration status
- [ ] Inactive credentials are clearly marked

**API Endpoint**: `GET /api/credentials`

**Response Example**:
```json
{
  "credentials": [
    {
      "id": 1,
      "platform": "linkedin",
      "account_name": "My Company LinkedIn",
      "token_expires_at": "2026-03-27T00:00:00Z",
      "is_active": true,
      "created_at": "2026-01-27T18:00:00Z"
    },
    {
      "id": 2,
      "platform": "facebook",
      "account_name": "My Business Page",
      "token_expires_at": "2026-02-27T00:00:00Z",
      "is_active": true,
      "created_at": "2026-01-27T18:05:00Z"
    }
  ]
}
```

#### Story 1.3: Validate Credentials
**As a** user
**I want to** verify my stored credentials are still valid
**So that** I can proactively update expired tokens

**Acceptance Criteria**:
- [ ] User can trigger validation for specific credential
- [ ] System makes test API call to platform
- [ ] Response indicates success or failure with error details
- [ ] Credential is marked inactive if validation fails
- [ ] Validation respects platform API rate limits

**API Endpoint**: `POST /api/credentials/{id}/validate`

**Response Example**:
```json
{
  "valid": true,
  "message": "Credential validated successfully",
  "last_validated_at": "2026-01-27T18:30:00Z"
}
```

#### Story 1.4: Update Credentials
**As a** user
**I want to** update expired or invalid tokens
**So that** I can maintain continuous publishing capability

**Acceptance Criteria**:
- [ ] User can update access token
- [ ] New token is re-encrypted before storage
- [ ] System validates new token before accepting
- [ ] Account name and metadata can be updated
- [ ] Updated timestamp is recorded

**API Endpoint**: `PUT /api/credentials/{id}`

#### Story 1.5: Delete Credentials
**As a** user
**I want to** remove credentials I no longer need
**So that** I can maintain a clean credential list

**Acceptance Criteria**:
- [ ] User can delete credential by ID
- [ ] Deletion removes encrypted token from database
- [ ] System warns if credential is actively used in scheduled posts
- [ ] Soft delete option to preserve historical data
- [ ] Hard delete permanently removes all data

**API Endpoint**: `DELETE /api/credentials/{id}`

---

### 2.2 Epic 2: Post Management

#### Story 2.1: Create Draft Post
**As a** user
**I want to** create a post in draft status
**So that** I can review and edit content before publishing

**Acceptance Criteria**:
- [ ] User can create post with text content
- [ ] Optional image URL can be provided
- [ ] Post defaults to "draft" status
- [ ] Timestamp is automatically recorded
- [ ] Post is stored in database immediately

**API Endpoint**: `POST /api/posts`

**Request Example**:
```json
{
  "content_text": "Excited to announce our new product launch! 🚀",
  "content_image_url": "https://example.com/images/product.jpg"
}
```

**Response Example**:
```json
{
  "id": 1,
  "content_text": "Excited to announce our new product launch! 🚀",
  "content_image_url": "https://example.com/images/product.jpg",
  "status": "draft",
  "created_at": "2026-01-27T18:00:00Z",
  "updated_at": "2026-01-27T18:00:00Z"
}
```

#### Story 2.2: List All Posts
**As a** user
**I want to** view all my posts with filtering options
**So that** I can manage my content pipeline

**Acceptance Criteria**:
- [ ] User can retrieve paginated list of posts
- [ ] Filter by status (draft, scheduled, published, failed)
- [ ] Filter by platform publication status
- [ ] Sort by creation date or scheduled time
- [ ] Response includes publication status for each platform

**API Endpoint**: `GET /api/posts?status=draft&limit=20&offset=0`

**Response Example**:
```json
{
  "posts": [
    {
      "id": 1,
      "content_text": "Exciting news coming soon!",
      "status": "draft",
      "created_at": "2026-01-27T18:00:00Z",
      "facebook_status": null,
      "linkedin_status": null
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

#### Story 2.3: Get Single Post
**As a** user
**I want to** view detailed information for a specific post
**So that** I can see full publication status across platforms

**Acceptance Criteria**:
- [ ] User can retrieve post by ID
- [ ] Response includes full content and metadata
- [ ] Platform-specific post IDs are included
- [ ] Publication timestamps for each platform shown
- [ ] Error messages for failed publications included

**API Endpoint**: `GET /api/posts/{id}`

**Response Example**:
```json
{
  "id": 1,
  "content_text": "Product launch announcement",
  "content_image_url": "https://example.com/images/product.jpg",
  "status": "published",
  "created_at": "2026-01-27T18:00:00Z",
  "updated_at": "2026-01-27T18:10:00Z",
  "facebook_post_id": "123456789_987654321",
  "facebook_published_at": "2026-01-27T18:10:00Z",
  "facebook_status": "success",
  "facebook_error": null,
  "linkedin_post_id": "urn:li:share:7123456789",
  "linkedin_published_at": "2026-01-27T18:10:05Z",
  "linkedin_status": "success",
  "linkedin_error": null
}
```

#### Story 2.4: Update Draft Post
**As a** user
**I want to** edit post content before publishing
**So that** I can refine my message

**Acceptance Criteria**:
- [ ] User can update content_text
- [ ] User can update content_image_url
- [ ] Only draft posts can be fully edited
- [ ] Published posts cannot be edited (platform limitation)
- [ ] Updated timestamp is recorded

**API Endpoint**: `PUT /api/posts/{id}`

**Request Example**:
```json
{
  "content_text": "Updated: Even more exciting news!",
  "content_image_url": "https://example.com/images/updated.jpg"
}
```

#### Story 2.5: Delete Post
**As a** user
**I want to** delete posts from my system
**So that** I can clean up unwanted drafts

**Acceptance Criteria**:
- [ ] User can delete post by ID
- [ ] Draft posts are immediately deleted
- [ ] Published posts deletion does not affect platform posts
- [ ] Scheduled posts are cancelled before deletion
- [ ] Confirmation is required for published posts

**API Endpoint**: `DELETE /api/posts/{id}`

**Response Example**:
```json
{
  "message": "Post deleted successfully",
  "id": 1
}
```

---

### 2.3 Epic 3: Post Publishing

#### Story 3.1: Publish Post Immediately (Text Only)
**As a** user
**I want to** publish a text post to Facebook and LinkedIn immediately
**So that** my content reaches both audiences at once

**Acceptance Criteria**:
- [ ] User triggers publication for specific post ID
- [ ] System retrieves active credentials for both platforms
- [ ] Post is published to Facebook using `/feed` endpoint
- [ ] Post is published to LinkedIn using `/rest/posts` endpoint
- [ ] Platform-specific post IDs are stored in database
- [ ] Publication timestamps are recorded
- [ ] Overall post status updated to "published"
- [ ] Individual platform statuses updated independently
- [ ] Error handling captures failures without blocking other platforms

**API Endpoint**: `POST /api/posts/{id}/publish`

**Request Example**:
```json
{
  "platforms": ["facebook", "linkedin"]
}
```

**Response Example**:
```json
{
  "id": 1,
  "status": "published",
  "results": {
    "facebook": {
      "success": true,
      "post_id": "123456789_987654321",
      "published_at": "2026-01-27T18:10:00Z"
    },
    "linkedin": {
      "success": true,
      "post_id": "urn:li:share:7123456789",
      "published_at": "2026-01-27T18:10:05Z"
    }
  }
}
```

**Technical Flow**:
1. Validate post exists and is in "draft" or "scheduled" status
2. Retrieve active credentials for requested platforms
3. Decrypt access tokens
4. For Facebook:
   - POST to `https://graph.facebook.com/v24.0/{page-id}/feed`
   - Include `message` parameter with `content_text`
   - Capture response `id` field
5. For LinkedIn:
   - POST to `https://api.linkedin.com/rest/posts`
   - Include headers: `Authorization`, `LinkedIn-Version: 202601`, `X-Restli-Protocol-Version: 2.0.0`
   - Body: `{"author": "urn:li:...", "commentary": "...", "visibility": "PUBLIC", ...}`
   - Capture response header `x-restli-id`
6. Update database with platform post IDs and timestamps
7. Set overall status to "published"
8. Return aggregated results

#### Story 3.2: Publish Post with Image
**As a** user
**I want to** publish a post with an image to both platforms
**So that** my visual content is shared across networks

**Acceptance Criteria**:
- [ ] User provides post with content_image_url
- [ ] For Facebook: POST to `/{page-id}/photos` endpoint
- [ ] For LinkedIn: Two-step upload process
  - Step 1: Initialize upload via `/rest/images?action=initializeUpload`
  - Step 2: Upload binary to provided URL
  - Step 3: Reference image URN in post
- [ ] Image downloads handled asynchronously
- [ ] Image format validation (JPEG, PNG)
- [ ] Maximum file size enforced (10MB)
- [ ] Fallback to text-only if image fails

**API Endpoint**: `POST /api/posts/{id}/publish`

**LinkedIn Image Upload Flow**:
```
1. POST /rest/images?action=initializeUpload
   Body: {"initializeUploadRequest": {"owner": "urn:li:organization:..."}}
   Response: {"value": {"uploadUrl": "...", "image": "urn:li:image:..."}}

2. POST {uploadUrl}
   Headers: Authorization: Bearer {token}
   Body: Binary image data

3. POST /rest/posts
   Body: {
     "commentary": "...",
     "content": {
       "media": {
         "id": "urn:li:image:..."
       }
     },
     ...
   }
```

**Facebook Image Upload**:
```
POST /{page-id}/photos
Body: {
  "url": "https://example.com/image.jpg",
  "message": "Post caption",
  "access_token": "..."
}
```

#### Story 3.3: Schedule Post for Future Publication
**As a** user
**I want to** schedule a post for future publication
**So that** I can plan my content calendar in advance

**Acceptance Criteria**:
- [ ] User specifies future datetime for publication
- [ ] Post status updated to "scheduled"
- [ ] Scheduled time stored in database
- [ ] Background worker checks for pending scheduled posts
- [ ] Post automatically published at scheduled time
- [ ] User can cancel scheduled post before publication
- [ ] User can reschedule to different time

**API Endpoint**: `POST /api/posts/{id}/schedule`

**Request Example**:
```json
{
  "scheduled_at": "2026-01-28T10:00:00Z",
  "platforms": ["facebook", "linkedin"]
}
```

**Response Example**:
```json
{
  "id": 1,
  "status": "scheduled",
  "scheduled_at": "2026-01-28T10:00:00Z",
  "platforms": ["facebook", "linkedin"]
}
```

**MVP Note**: Scheduling functionality is documented but may be implemented with a simple approach (manual trigger or basic cron job) rather than full background worker system.

#### Story 3.4: Check Publication Status
**As a** user
**I want to** check the current status of a published post
**So that** I can verify successful publication or identify issues

**Acceptance Criteria**:
- [ ] User can query status for specific post
- [ ] Response shows status for each platform
- [ ] Platform post IDs included for reference
- [ ] Error messages displayed if publication failed
- [ ] Timestamps for each publication attempt shown

**API Endpoint**: `GET /api/posts/{id}/status`

**Response Example**:
```json
{
  "id": 1,
  "overall_status": "published",
  "platforms": {
    "facebook": {
      "status": "success",
      "post_id": "123456789_987654321",
      "published_at": "2026-01-27T18:10:00Z",
      "error": null,
      "url": "https://facebook.com/123456789/posts/987654321"
    },
    "linkedin": {
      "status": "failed",
      "post_id": null,
      "published_at": null,
      "error": "Invalid access token - token may be expired",
      "retry_count": 2
    }
  }
}
```

---

## 3. Technical Implementation Plan

### 3.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         FastAPI Application                  │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼────────┐   ┌────────▼────────┐   ┌──────▼──────┐
│   Credential   │   │      Post       │   │   Status    │
│    Router      │   │     Router      │   │   Router    │
└───────┬────────┘   └────────┬────────┘   └──────┬──────┘
        │                     │                    │
        └─────────────────────┼────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  Publisher Service │
                    └─────────┬──────────┘
                              │
                ┌─────────────┼─────────────┐
                │                           │
        ┌───────▼────────┐         ┌───────▼────────┐
        │    Facebook    │         │    LinkedIn    │
        │    Adapter     │         │    Adapter     │
        └───────┬────────┘         └───────┬────────┘
                │                           │
                └─────────────┬─────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   HTTPX Client     │
                    │  (Async HTTP)      │
                    └─────────┬──────────┘
                              │
            ┌─────────────────┼─────────────────┐
            │                                   │
    ┌───────▼────────┐                 ┌───────▼────────┐
    │  Facebook API  │                 │  LinkedIn API  │
    │   (Graph v24)  │                 │  (REST /posts) │
    └────────────────┘                 └────────────────┘
```

### 3.2 Technology Stack Implementation

#### 3.2.1 Core Dependencies (requirements.txt)
```txt
# Core Framework
fastapi>=0.109.0
uvicorn[standard]>=0.27.0

# Database & ORM
sqlmodel>=0.0.14
sqlalchemy[asyncio]>=2.0.25
aiosqlite>=0.19.0

# HTTP Client
httpx>=0.26.0

# Security & Encryption
cryptography>=41.0.7

# File Upload Support
python-multipart>=0.0.6

# Environment Variables
python-dotenv>=1.0.0

# Testing (Optional)
pytest>=7.4.3
pytest-asyncio>=0.23.3
httpx-mock>=0.15.0
```

#### 3.2.2 Environment Configuration (.env)
```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./data/social_hub.db

# Security
ENCRYPTION_KEY=<base64-fernet-key>

# App Settings
DEBUG=true
HOST=0.0.0.0
PORT=8000

# Platform Credentials (for testing)
FACEBOOK_API_VERSION=v24.0
FACEBOOK_PAGE_ID=
FACEBOOK_PAGE_ACCESS_TOKEN=

LINKEDIN_API_VERSION=202601
LINKEDIN_ORGANIZATION_URN=
LINKEDIN_ACCESS_TOKEN=
```

---

### 3.3 Files to Create

#### Phase 1: Foundation Layer

##### File: `app/__init__.py`
```python
"""Social Media Hub Application"""
__version__ = "1.0.0"
```

##### File: `app/config.py`
```python
"""Application configuration"""
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite+aiosqlite:///./data/social_hub.db"

    # Security
    encryption_key: str

    # Application
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000

    # Facebook
    facebook_api_version: str = "v24.0"
    facebook_base_url: str = "https://graph.facebook.com"

    # LinkedIn
    linkedin_api_version: str = "202601"
    linkedin_base_url: str = "https://api.linkedin.com/rest"

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

##### File: `app/database.py`
```python
"""Async database configuration"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlmodel import SQLModel
from app.config import get_settings

settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def create_db_and_tables():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_async_session():
    """FastAPI dependency for database sessions"""
    async with async_session_maker() as session:
        yield session
```

---

#### Phase 2: Data Models

##### File: `app/models/__init__.py`
```python
"""Database models"""
from app.models.credential import SocialCredential
from app.models.post import SocialPost

__all__ = ["SocialCredential", "SocialPost"]
```

##### File: `app/models/credential.py`
```python
"""SocialCredential model"""
from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional

class SocialCredential(SQLModel, table=True):
    """Stores encrypted social media platform credentials"""

    __tablename__ = "social_credentials"

    id: Optional[int] = Field(default=None, primary_key=True)
    platform: str = Field(index=True)  # "facebook" or "linkedin"
    account_name: str
    encrypted_token: str
    token_expires_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

##### File: `app/models/post.py`
```python
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
```

---

#### Phase 3: Pydantic Schemas

##### File: `app/schemas/credential.py`
```python
"""Pydantic schemas for credentials"""
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class CredentialBase(BaseModel):
    platform: str = Field(..., pattern="^(facebook|linkedin)$")
    account_name: str

class CredentialCreate(CredentialBase):
    access_token: str
    token_expires_at: Optional[datetime] = None

class CredentialUpdate(BaseModel):
    account_name: Optional[str] = None
    access_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None

class CredentialPublic(CredentialBase):
    id: int
    token_expires_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CredentialValidation(BaseModel):
    valid: bool
    message: str
    last_validated_at: datetime
```

##### File: `app/schemas/post.py`
```python
"""Pydantic schemas for posts"""
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

class PostBase(BaseModel):
    content_text: str = Field(..., min_length=1, max_length=3000)
    content_image_url: Optional[HttpUrl] = None

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    content_text: Optional[str] = Field(None, min_length=1, max_length=3000)
    content_image_url: Optional[HttpUrl] = None

class PostPublic(PostBase):
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
    platforms: List[str] = Field(default=["facebook", "linkedin"])

class PostSchedule(BaseModel):
    scheduled_at: datetime
    platforms: List[str] = Field(default=["facebook", "linkedin"])

class PlatformStatus(BaseModel):
    status: str
    post_id: Optional[str]
    published_at: Optional[datetime]
    error: Optional[str]

class PostStatusResponse(BaseModel):
    id: int
    overall_status: str
    platforms: dict[str, PlatformStatus]
```

---

#### Phase 4: Encryption Service

##### File: `app/services/encryption.py`
```python
"""Token encryption service using Fernet"""
from cryptography.fernet import Fernet
from app.config import get_settings

settings = get_settings()

class EncryptionService:
    """Handles encryption and decryption of sensitive tokens"""

    def __init__(self):
        self.cipher = Fernet(settings.encryption_key.encode())

    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string"""
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a ciphertext string"""
        return self.cipher.decrypt(ciphertext.encode()).decode()

def get_encryption_service() -> EncryptionService:
    """Dependency for encryption service"""
    return EncryptionService()
```

---

#### Phase 5: Platform Adapters

##### File: `app/adapters/base.py`
```python
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
```

##### File: `app/adapters/facebook.py`
```python
"""Facebook Graph API adapter"""
import httpx
from typing import Optional
from app.adapters.base import BaseSocialAdapter
from app.config import get_settings

settings = get_settings()

class FacebookAdapter(BaseSocialAdapter):
    """Implements BaseSocialAdapter for Facebook Graph API v24.0"""

    def __init__(self):
        self.base_url = f"{settings.facebook_base_url}/{settings.facebook_api_version}"

    async def validate_credentials(self, token: str) -> bool:
        """Validate Facebook Page Access Token"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/me",
                    params={"access_token": token}
                )
                return response.status_code == 200
            except Exception:
                return False

    async def publish_post(
        self,
        token: str,
        content: str,
        image_url: Optional[str] = None,
        page_id: Optional[str] = None
    ) -> dict:
        """
        Publish post to Facebook

        Uses /{page-id}/feed for text posts
        Uses /{page-id}/photos for posts with images
        """
        if not page_id:
            return {"success": False, "post_id": None, "error": "page_id required"}

        async with httpx.AsyncClient() as client:
            try:
                if image_url:
                    # POST to /photos endpoint for image posts
                    endpoint = f"{self.base_url}/{page_id}/photos"
                    data = {
                        "url": image_url,
                        "message": content,
                        "access_token": token
                    }
                else:
                    # POST to /feed endpoint for text posts
                    endpoint = f"{self.base_url}/{page_id}/feed"
                    data = {
                        "message": content,
                        "access_token": token
                    }

                response = await client.post(endpoint, data=data)

                if response.status_code in [200, 201]:
                    result = response.json()
                    post_id = result.get("post_id") or result.get("id")
                    return {
                        "success": True,
                        "post_id": post_id,
                        "error": None
                    }
                else:
                    error_data = response.json()
                    return {
                        "success": False,
                        "post_id": None,
                        "error": error_data.get("error", {}).get("message", "Unknown error")
                    }
            except Exception as e:
                return {
                    "success": False,
                    "post_id": None,
                    "error": str(e)
                }

    async def delete_post(self, token: str, post_id: str) -> bool:
        """Delete a Facebook post"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{self.base_url}/{post_id}",
                    params={"access_token": token}
                )
                return response.status_code == 200
            except Exception:
                return False

    async def get_post_status(self, token: str, post_id: str) -> dict:
        """Get Facebook post status"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/{post_id}",
                    params={
                        "access_token": token,
                        "fields": "id,message,created_time"
                    }
                )
                if response.status_code == 200:
                    return {
                        "exists": True,
                        "data": response.json()
                    }
                return {"exists": False, "data": None}
            except Exception:
                return {"exists": False, "data": None}
```

##### File: `app/adapters/linkedin.py`
```python
"""LinkedIn REST API adapter"""
import httpx
from typing import Optional
from app.adapters.base import BaseSocialAdapter
from app.config import get_settings

settings = get_settings()

class LinkedInAdapter(BaseSocialAdapter):
    """Implements BaseSocialAdapter for LinkedIn REST API"""

    def __init__(self):
        self.base_url = settings.linkedin_base_url
        self.api_version = settings.linkedin_api_version

    def _get_headers(self, token: str) -> dict:
        """Get required headers for LinkedIn API"""
        return {
            "Authorization": f"Bearer {token}",
            "LinkedIn-Version": self.api_version,
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }

    async def validate_credentials(self, token: str) -> bool:
        """Validate LinkedIn access token"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://api.linkedin.com/v2/userinfo",
                    headers={"Authorization": f"Bearer {token}"}
                )
                return response.status_code == 200
            except Exception:
                return False

    async def publish_post(
        self,
        token: str,
        content: str,
        image_url: Optional[str] = None,
        author_urn: Optional[str] = None
    ) -> dict:
        """
        Publish post to LinkedIn using /rest/posts endpoint

        For images, uses two-step upload:
        1. Initialize upload via /rest/images?action=initializeUpload
        2. Upload binary to provided URL
        3. Reference image URN in post
        """
        if not author_urn:
            return {"success": False, "post_id": None, "error": "author_urn required"}

        async with httpx.AsyncClient() as client:
            try:
                # Build post payload
                payload = {
                    "author": author_urn,
                    "commentary": content,
                    "visibility": "PUBLIC",
                    "distribution": {
                        "feedDistribution": "MAIN_FEED",
                        "targetEntities": [],
                        "thirdPartyDistributionChannels": []
                    },
                    "lifecycleState": "PUBLISHED",
                    "isReshareDisabledByAuthor": False
                }

                # Handle image upload if provided
                if image_url:
                    image_urn = await self._upload_image(client, token, image_url, author_urn)
                    if image_urn:
                        payload["content"] = {
                            "media": {
                                "id": image_urn
                            }
                        }

                # Publish post
                response = await client.post(
                    f"{self.base_url}/posts",
                    json=payload,
                    headers=self._get_headers(token)
                )

                if response.status_code == 201:
                    # Post ID is in x-restli-id header
                    post_id = response.headers.get("x-restli-id")
                    return {
                        "success": True,
                        "post_id": post_id,
                        "error": None
                    }
                else:
                    error_data = response.json()
                    return {
                        "success": False,
                        "post_id": None,
                        "error": error_data.get("message", "Unknown error")
                    }
            except Exception as e:
                return {
                    "success": False,
                    "post_id": None,
                    "error": str(e)
                }

    async def _upload_image(
        self,
        client: httpx.AsyncClient,
        token: str,
        image_url: str,
        owner_urn: str
    ) -> Optional[str]:
        """
        Two-step image upload process for LinkedIn

        Returns image URN on success, None on failure
        """
        try:
            # Step 1: Initialize upload
            init_response = await client.post(
                f"{self.base_url}/images?action=initializeUpload",
                json={
                    "initializeUploadRequest": {
                        "owner": owner_urn
                    }
                },
                headers=self._get_headers(token)
            )

            if init_response.status_code != 200:
                return None

            init_data = init_response.json()
            upload_url = init_data["value"]["uploadUrl"]
            image_urn = init_data["value"]["image"]

            # Step 2: Download image from URL
            image_response = await client.get(image_url)
            if image_response.status_code != 200:
                return None

            # Step 3: Upload binary data
            upload_response = await client.post(
                upload_url,
                content=image_response.content,
                headers={"Authorization": f"Bearer {token}"}
            )

            if upload_response.status_code in [200, 201]:
                return image_urn

            return None
        except Exception:
            return None

    async def delete_post(self, token: str, post_id: str) -> bool:
        """Delete a LinkedIn post"""
        # LinkedIn REST API delete implementation
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{self.base_url}/posts/{post_id}",
                    headers=self._get_headers(token)
                )
                return response.status_code == 204
            except Exception:
                return False

    async def get_post_status(self, token: str, post_id: str) -> dict:
        """Get LinkedIn post status"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/posts/{post_id}",
                    headers=self._get_headers(token)
                )
                if response.status_code == 200:
                    return {
                        "exists": True,
                        "data": response.json()
                    }
                return {"exists": False, "data": None}
            except Exception:
                return {"exists": False, "data": None}
```

---

#### Phase 6: Publisher Service

##### File: `app/services/publisher.py`
```python
"""Publishing orchestration service"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.models.post import SocialPost
from app.models.credential import SocialCredential
from app.adapters.facebook import FacebookAdapter
from app.adapters.linkedin import LinkedInAdapter
from app.services.encryption import EncryptionService

class PublisherService:
    """Orchestrates publishing to multiple platforms"""

    def __init__(self, session: AsyncSession, encryption_service: EncryptionService):
        self.session = session
        self.encryption = encryption_service
        self.facebook_adapter = FacebookAdapter()
        self.linkedin_adapter = LinkedInAdapter()

    async def publish_post(
        self,
        post_id: int,
        platforms: List[str]
    ) -> dict:
        """
        Publish a post to specified platforms

        Returns aggregated results for all platforms
        """
        # Get post
        result = await self.session.execute(
            select(SocialPost).where(SocialPost.id == post_id)
        )
        post = result.scalar_one_or_none()

        if not post:
            return {"error": "Post not found"}

        results = {}

        # Publish to each platform
        if "facebook" in platforms:
            fb_result = await self._publish_to_facebook(post)
            results["facebook"] = fb_result

            # Update post with Facebook results
            post.facebook_status = "success" if fb_result["success"] else "failed"
            post.facebook_post_id = fb_result.get("post_id")
            post.facebook_published_at = datetime.utcnow() if fb_result["success"] else None
            post.facebook_error = fb_result.get("error")

        if "linkedin" in platforms:
            li_result = await self._publish_to_linkedin(post)
            results["linkedin"] = li_result

            # Update post with LinkedIn results
            post.linkedin_status = "success" if li_result["success"] else "failed"
            post.linkedin_post_id = li_result.get("post_id")
            post.linkedin_published_at = datetime.utcnow() if li_result["success"] else None
            post.linkedin_error = li_result.get("error")

        # Update overall post status
        all_success = all(r.get("success") for r in results.values())
        post.status = "published" if all_success else "failed"
        post.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(post)

        return {
            "id": post.id,
            "status": post.status,
            "results": results
        }

    async def _publish_to_facebook(self, post: SocialPost) -> dict:
        """Publish to Facebook"""
        # Get active Facebook credential
        result = await self.session.execute(
            select(SocialCredential).where(
                SocialCredential.platform == "facebook",
                SocialCredential.is_active == True
            )
        )
        credential = result.first()

        if not credential:
            return {
                "success": False,
                "post_id": None,
                "error": "No active Facebook credential found"
            }

        # Decrypt token
        token = self.encryption.decrypt(credential[0].encrypted_token)

        # Publish via adapter
        return await self.facebook_adapter.publish_post(
            token=token,
            content=post.content_text,
            image_url=post.content_image_url,
            page_id=None  # Should be retrieved from credential or config
        )

    async def _publish_to_linkedin(self, post: SocialPost) -> dict:
        """Publish to LinkedIn"""
        # Get active LinkedIn credential
        result = await self.session.execute(
            select(SocialCredential).where(
                SocialCredential.platform == "linkedin",
                SocialCredential.is_active == True
            )
        )
        credential = result.first()

        if not credential:
            return {
                "success": False,
                "post_id": None,
                "error": "No active LinkedIn credential found"
            }

        # Decrypt token
        token = self.encryption.decrypt(credential[0].encrypted_token)

        # Publish via adapter
        return await self.linkedin_adapter.publish_post(
            token=token,
            content=post.content_text,
            image_url=post.content_image_url,
            author_urn=None  # Should be retrieved from credential or config
        )
```

---

#### Phase 7: API Routers

##### File: `app/routers/credentials.py`
```python
"""Credential management endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from typing import List
from datetime import datetime

from app.database import get_async_session
from app.models.credential import SocialCredential
from app.schemas.credential import (
    CredentialCreate,
    CredentialUpdate,
    CredentialPublic,
    CredentialValidation
)
from app.services.encryption import get_encryption_service, EncryptionService
from app.adapters.facebook import FacebookAdapter
from app.adapters.linkedin import LinkedInAdapter

router = APIRouter(prefix="/api/credentials", tags=["credentials"])

@router.post("/", response_model=CredentialPublic, status_code=201)
async def create_credential(
    *,
    session: AsyncSession = Depends(get_async_session),
    credential: CredentialCreate,
    encryption: EncryptionService = Depends(get_encryption_service)
):
    """Create new platform credential"""
    # Validate token before saving
    is_valid = await _validate_token(credential.platform, credential.access_token)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid access token")

    # Encrypt token
    encrypted_token = encryption.encrypt(credential.access_token)

    # Create credential
    db_credential = SocialCredential(
        platform=credential.platform,
        account_name=credential.account_name,
        encrypted_token=encrypted_token,
        token_expires_at=credential.token_expires_at
    )

    session.add(db_credential)
    await session.commit()
    await session.refresh(db_credential)

    return db_credential

@router.get("/", response_model=List[CredentialPublic])
async def list_credentials(
    *,
    session: AsyncSession = Depends(get_async_session)
):
    """List all credentials"""
    result = await session.execute(select(SocialCredential))
    credentials = result.scalars().all()
    return credentials

@router.get("/{credential_id}", response_model=CredentialPublic)
async def get_credential(
    *,
    session: AsyncSession = Depends(get_async_session),
    credential_id: int
):
    """Get specific credential"""
    result = await session.execute(
        select(SocialCredential).where(SocialCredential.id == credential_id)
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    return credential

@router.put("/{credential_id}", response_model=CredentialPublic)
async def update_credential(
    *,
    session: AsyncSession = Depends(get_async_session),
    credential_id: int,
    credential_update: CredentialUpdate,
    encryption: EncryptionService = Depends(get_encryption_service)
):
    """Update credential"""
    result = await session.execute(
        select(SocialCredential).where(SocialCredential.id == credential_id)
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    # Update fields
    if credential_update.account_name:
        credential.account_name = credential_update.account_name

    if credential_update.access_token:
        # Validate new token
        is_valid = await _validate_token(credential.platform, credential_update.access_token)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid access token")

        credential.encrypted_token = encryption.encrypt(credential_update.access_token)

    if credential_update.token_expires_at is not None:
        credential.token_expires_at = credential_update.token_expires_at

    if credential_update.is_active is not None:
        credential.is_active = credential_update.is_active

    credential.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(credential)

    return credential

@router.delete("/{credential_id}", status_code=204)
async def delete_credential(
    *,
    session: AsyncSession = Depends(get_async_session),
    credential_id: int
):
    """Delete credential"""
    result = await session.execute(
        select(SocialCredential).where(SocialCredential.id == credential_id)
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    await session.delete(credential)
    await session.commit()

    return None

@router.post("/{credential_id}/validate", response_model=CredentialValidation)
async def validate_credential(
    *,
    session: AsyncSession = Depends(get_async_session),
    credential_id: int,
    encryption: EncryptionService = Depends(get_encryption_service)
):
    """Validate credential with platform"""
    result = await session.execute(
        select(SocialCredential).where(SocialCredential.id == credential_id)
    )
    credential = result.scalar_one_or_none()

    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    # Decrypt token
    token = encryption.decrypt(credential.encrypted_token)

    # Validate
    is_valid = await _validate_token(credential.platform, token)

    return CredentialValidation(
        valid=is_valid,
        message="Credential is valid" if is_valid else "Credential validation failed",
        last_validated_at=datetime.utcnow()
    )

async def _validate_token(platform: str, token: str) -> bool:
    """Helper to validate token with platform adapter"""
    if platform == "facebook":
        adapter = FacebookAdapter()
    elif platform == "linkedin":
        adapter = LinkedInAdapter()
    else:
        return False

    return await adapter.validate_credentials(token)
```

##### File: `app/routers/posts.py`
```python
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
```

---

#### Phase 8: Main Application

##### File: `app/main.py`
```python
"""FastAPI application entry point"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import create_db_and_tables
from app.routers import credentials, posts
from app.config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await create_db_and_tables()
    yield
    # Shutdown (cleanup if needed)

app = FastAPI(
    title="Social Media Hub API",
    description="Lightweight social media management platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(credentials.router)
app.include_router(posts.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Social Media Hub API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
```

---

### 3.4 Database Schema

```sql
-- social_credentials table
CREATE TABLE social_credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform VARCHAR NOT NULL,
    account_name VARCHAR NOT NULL,
    encrypted_token TEXT NOT NULL,
    token_expires_at DATETIME,
    is_active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_platform ON social_credentials(platform);

-- social_posts table
CREATE TABLE social_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_text TEXT NOT NULL,
    content_image_url TEXT,
    status VARCHAR DEFAULT 'draft',
    scheduled_at DATETIME,

    facebook_post_id VARCHAR,
    facebook_published_at DATETIME,
    facebook_status VARCHAR,
    facebook_error TEXT,

    linkedin_post_id VARCHAR,
    linkedin_published_at DATETIME,
    linkedin_status VARCHAR,
    linkedin_error TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_status ON social_posts(status);
CREATE INDEX idx_scheduled_at ON social_posts(scheduled_at);
```

---

## 4. Verification & Testing

### 4.1 Unit Tests

#### File: `tests/test_encryption.py`
```python
"""Tests for encryption service"""
import pytest
from app.services.encryption import EncryptionService

def test_encrypt_decrypt():
    """Test encryption and decryption"""
    service = EncryptionService()
    original = "test_token_12345"

    encrypted = service.encrypt(original)
    assert encrypted != original

    decrypted = service.decrypt(encrypted)
    assert decrypted == original
```

#### File: `tests/test_adapters.py`
```python
"""Tests for platform adapters"""
import pytest
import httpx
from httpx import Response
from app.adapters.facebook import FacebookAdapter
from app.adapters.linkedin import LinkedInAdapter

@pytest.mark.asyncio
async def test_facebook_publish_text_post(httpx_mock):
    """Test Facebook text post publishing"""
    httpx_mock.add_response(
        url="https://graph.facebook.com/v24.0/123/feed",
        json={"id": "123_456"},
        status_code=200
    )

    adapter = FacebookAdapter()
    result = await adapter.publish_post(
        token="test_token",
        content="Test post",
        page_id="123"
    )

    assert result["success"] is True
    assert result["post_id"] == "123_456"
    assert result["error"] is None

@pytest.mark.asyncio
async def test_linkedin_publish_text_post(httpx_mock):
    """Test LinkedIn text post publishing"""
    httpx_mock.add_response(
        url="https://api.linkedin.com/rest/posts",
        headers={"x-restli-id": "urn:li:share:123"},
        status_code=201
    )

    adapter = LinkedInAdapter()
    result = await adapter.publish_post(
        token="test_token",
        content="Test post",
        author_urn="urn:li:organization:123"
    )

    assert result["success"] is True
    assert result["post_id"] == "urn:li:share:123"
    assert result["error"] is None
```

---

### 4.2 Integration Tests

#### File: `tests/test_posts.py`
```python
"""Integration tests for post endpoints"""
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_post():
    """Test creating a draft post"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/posts/",
            json={
                "content_text": "Test post content",
                "content_image_url": "https://example.com/image.jpg"
            }
        )

    assert response.status_code == 201
    data = response.json()
    assert data["content_text"] == "Test post content"
    assert data["status"] == "draft"
    assert "id" in data

@pytest.mark.asyncio
async def test_list_posts():
    """Test listing posts"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/posts/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

---

### 4.3 Manual Testing Checklist

#### Credential Management Tests
- [ ] Create Facebook credential with valid token
- [ ] Create LinkedIn credential with valid token
- [ ] List all credentials (verify no plaintext tokens exposed)
- [ ] Validate credential (successful)
- [ ] Validate credential (failed/expired token)
- [ ] Update credential with new token
- [ ] Delete credential

#### Post Management Tests
- [ ] Create draft post (text only)
- [ ] Create draft post (text + image URL)
- [ ] List all posts
- [ ] Filter posts by status (draft, published)
- [ ] Get specific post by ID
- [ ] Update draft post content
- [ ] Attempt to update published post (should fail)
- [ ] Delete draft post
- [ ] Delete published post

#### Publishing Tests
- [ ] Publish text post to Facebook only
- [ ] Publish text post to LinkedIn only
- [ ] Publish text post to both platforms
- [ ] Publish post with image to Facebook
- [ ] Publish post with image to LinkedIn
- [ ] Publish post with image to both platforms
- [ ] Verify post appears on Facebook page
- [ ] Verify post appears on LinkedIn feed
- [ ] Check publication status endpoint
- [ ] Verify platform post IDs stored correctly
- [ ] Test error handling (invalid credentials)
- [ ] Test error handling (network failure)

#### Scheduling Tests (if implemented)
- [ ] Schedule post for future time
- [ ] List scheduled posts
- [ ] Cancel scheduled post
- [ ] Verify post publishes at scheduled time

---

### 4.4 Test Scenarios

#### Scenario 1: First-Time Setup
```bash
# 1. Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 2. Configure .env file with key

# 3. Start application
uvicorn app.main:app --reload

# 4. Access API docs
# Open http://localhost:8000/docs

# 5. Create Facebook credential
curl -X POST "http://localhost:8000/api/credentials/" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "facebook",
    "account_name": "My Business Page",
    "access_token": "YOUR_FB_PAGE_TOKEN"
  }'

# 6. Create LinkedIn credential
curl -X POST "http://localhost:8000/api/credentials/" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "linkedin",
    "account_name": "My Company",
    "access_token": "YOUR_LI_TOKEN"
  }'
```

#### Scenario 2: Publishing Text Post
```bash
# 1. Create draft post
curl -X POST "http://localhost:8000/api/posts/" \
  -H "Content-Type: application/json" \
  -d '{
    "content_text": "Excited to share our latest updates! 🚀"
  }'
# Response: {"id": 1, "status": "draft", ...}

# 2. Publish to both platforms
curl -X POST "http://localhost:8000/api/posts/1/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "platforms": ["facebook", "linkedin"]
  }'

# 3. Check status
curl "http://localhost:8000/api/posts/1/status"
```

#### Scenario 3: Publishing Post with Image
```bash
# 1. Create post with image
curl -X POST "http://localhost:8000/api/posts/" \
  -H "Content-Type: application/json" \
  -d '{
    "content_text": "Check out our new product!",
    "content_image_url": "https://example.com/product.jpg"
  }'

# 2. Publish
curl -X POST "http://localhost:8000/api/posts/2/publish" \
  -H "Content-Type: application/json" \
  -d '{
    "platforms": ["facebook", "linkedin"]
  }'

# 3. Verify on platforms
# - Check Facebook page for post with image
# - Check LinkedIn feed for post with image
```

#### Scenario 4: Error Handling
```bash
# 1. Try to publish with expired credentials
# Expected: Error message indicating token expiration

# 2. Try to publish to platform without credentials
# Expected: Error message "No active [platform] credential found"

# 3. Try to edit published post
# Expected: 400 error "Only draft posts can be edited"
```

---

## 5. Success Criteria Verification

### 5.1 Functional Requirements

| Requirement | Verification Method | Status |
|-------------|-------------------|--------|
| Store encrypted credentials | Create credential → Verify encrypted in DB | ⬜ |
| CRUD operations for posts | Test all endpoints | ⬜ |
| Publish text posts to Facebook | Manual verification on FB | ⬜ |
| Publish text posts to LinkedIn | Manual verification on LI | ⬜ |
| Publish image posts to Facebook | Manual verification on FB | ⬜ |
| Publish image posts to LinkedIn | Manual verification on LI | ⬜ |
| Track platform-specific status | Check status endpoint | ⬜ |
| Handle API errors gracefully | Test with invalid credentials | ⬜ |
| Store platform post IDs | Verify in database after publish | ⬜ |

### 5.2 Non-Functional Requirements

| Requirement | Verification Method | Target | Status |
|-------------|-------------------|--------|--------|
| API response time | Load testing | <1s for CRUD | ⬜ |
| Concurrent requests | Async load test | 10+ simultaneous | ⬜ |
| Token security | Code review + DB inspect | No plaintext tokens | ⬜ |
| Error logging | Review logs | All errors logged | ⬜ |
| API documentation | Check /docs endpoint | Complete & accurate | ⬜ |

---

## 6. Deployment Considerations

### 6.1 Environment Setup

```bash
# Production environment variables
DATABASE_URL=sqlite+aiosqlite:///./data/social_hub_prod.db
ENCRYPTION_KEY=<production-key>
DEBUG=false
HOST=0.0.0.0
PORT=8000

# Ensure data directory exists
mkdir -p data

# Run with production settings
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 6.2 Security Checklist

- [ ] Generate unique encryption key for production
- [ ] Store encryption key securely (not in code)
- [ ] Use environment variables for all sensitive data
- [ ] Enable HTTPS in production
- [ ] Configure CORS appropriately
- [ ] Set up rate limiting
- [ ] Implement request logging
- [ ] Regular credential rotation
- [ ] Database backups configured

---

## 7. Future Enhancements (Out of Scope for MVP)

### 7.1 Priority 1 (Next Version)
- Background worker for scheduled posts (Celery/RQ)
- OAuth2 flow for token acquisition
- Content length validation per platform
- Retry logic with exponential backoff
- Post preview before publishing

### 7.2 Priority 2
- Multi-user support with authentication
- Post analytics and engagement metrics
- Content calendar view
- Post templates
- Bulk operations

### 7.3 Priority 3
- Additional platforms (Twitter/X, Instagram)
- Video content support
- Hashtag suggestions
- AI-powered content optimization
- Webhook notifications

---

## 8. Open Questions & Decisions Needed

### 8.1 Image Storage Strategy
**Question**: Should images be stored locally or use external URLs only?

**Options**:
1. **External URLs only** (Current approach)
   - Pros: Simple, no storage management
   - Cons: Dependent on external hosting

2. **Local storage with upload endpoint**
   - Pros: Full control, reliability
   - Cons: Storage management, backup needed

**Recommendation**: Start with external URLs for MVP, add local storage in v1.1

### 8.2 Scheduling Implementation
**Question**: Use background worker or simple cron job for scheduled posts?

**Options**:
1. **Celery/RQ background worker**
   - Pros: Robust, scalable, retry logic
   - Cons: Additional complexity, Redis dependency

2. **Simple cron job**
   - Pros: Simple, no dependencies
   - Cons: Less reliable, no retry logic

**Recommendation**: Simple cron or manual trigger for MVP, Celery for production

### 8.3 Platform Configuration Storage
**Question**: Where to store platform-specific IDs (Facebook Page ID, LinkedIn Org URN)?

**Options**:
1. **In credential record** (extend model)
2. **Separate configuration table**
3. **Environment variables only**

**Recommendation**: Extend credential model to include platform_specific_id field

### 8.4 Content Validation
**Question**: Should we validate post content length limits per platform?

**Limits**:
- Facebook: 63,206 characters
- LinkedIn: 3,000 characters

**Recommendation**: Add validation in v1.1 after MVP validation

---

## 9. Appendix

### 9.1 API Payload Examples

#### LinkedIn POST /rest/posts (Text Only)
```json
{
  "author": "urn:li:organization:123456",
  "commentary": "Excited to announce our new product launch!",
  "visibility": "PUBLIC",
  "distribution": {
    "feedDistribution": "MAIN_FEED",
    "targetEntities": [],
    "thirdPartyDistributionChannels": []
  },
  "lifecycleState": "PUBLISHED",
  "isReshareDisabledByAuthor": false
}
```

#### LinkedIn POST /rest/posts (With Image)
```json
{
  "author": "urn:li:organization:123456",
  "commentary": "Check out this image!",
  "content": {
    "media": {
      "id": "urn:li:image:D4E18AQGw3P..."
    }
  },
  "visibility": "PUBLIC",
  "distribution": {
    "feedDistribution": "MAIN_FEED"
  },
  "lifecycleState": "PUBLISHED",
  "isReshareDisabledByAuthor": false
}
```

#### Facebook POST /{page-id}/feed (Text Only)
```bash
POST https://graph.facebook.com/v24.0/{PAGE_ID}/feed
Content-Type: application/x-www-form-urlencoded

message=Excited to announce our new product launch!&access_token=YOUR_PAGE_TOKEN
```

#### Facebook POST /{page-id}/photos (With Image)
```bash
POST https://graph.facebook.com/v24.0/{PAGE_ID}/photos
Content-Type: application/x-www-form-urlencoded

url=https://example.com/image.jpg&message=Check out this image!&access_token=YOUR_PAGE_TOKEN
```

---

## 10. Document Control

**Version History**:
- v1.0 (2026-01-27): Initial PRD based on INITIAL.md v1.1

**Approvals Required**:
- [ ] Product Owner
- [ ] Technical Lead
- [ ] Security Review

**Next Steps After Approval**:
1. Review and approve PRD
2. Begin Phase 1 implementation (Foundation)
3. Set up CI/CD pipeline
4. Configure development environment

---

**Document Status**: ✅ Ready for Review
**Generated**: 2026-01-27
**Source**: INITIAL.md v1.1
