# Project: Social Media Hub (Headless CMS + API)

> **Unified Content Management & Cross-Platform Publishing System**
> Built with Django 5, Wagtail CMS, and Django Ninja

---

## 1. Project Overview

### Goal
Build a centralized headless CMS that enables content creators to:
- Author rich content once in a unified interface
- Publish simultaneously to LinkedIn, Facebook, and LINE
- Track post status and engagement across platforms
- Manage audience data and credentials securely

### Core Philosophy: Database-First Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Local Database                            │
│                  (Single Source of Truth)                    │
│         SQLite (Dev) / PostgreSQL (Prod)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │Wagtail  │    │  Ninja  │    │ Celery  │
    │Editor UI│    │ API GW  │    │ Workers │
    └─────────┘    └─────────┘    └─────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐    ┌──────────┐   ┌─────────┐
    │Facebook │    │ LinkedIn │   │  LINE   │
    │Graph API│    │Posts API │   │Messaging│
    └─────────┘    └──────────┘   └─────────┘
```

**Key Principles**:
1. **Local DB is authoritative** - All post history, status, and metadata stored locally
2. **Platform APIs are integration targets** - External platforms are treated as downstream consumers
3. **Async-first** - All external API calls happen asynchronously via Celery
4. **Resilient by design** - Failed publishes are retried; status is always tracked

---

## 2. Tech Stack & Infrastructure

### Core Framework Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Backend Framework** | Django | 5.x | ORM, Admin, Security |
| **API Framework** | Django Ninja | Latest | Async REST API with Pydantic validation |
| **CMS** | Wagtail | Latest | Headless content management, StreamField |
| **Database (Dev)** | SQLite | 3.x | ✅ **Rapid development, zero config** |
| **Database (Prod)** | PostgreSQL | 14+ | Required for JSONField, full-text search, concurrency |
| **Task Queue** | Celery | 5.x | Async job processing |
| **Message Broker** | Redis | 7.x | Celery broker + result backend |
| **Python** | Python | 3.11+ | Async/await, type hints |

### Database Strategy

**Development Environment** ✅:
- **Use SQLite** for rapid development
- Zero configuration required
- Fast iteration cycles
- Perfect for single-developer setup

**Production Environment** ⚠️:
- **Use PostgreSQL** for production deployments
- Required for Wagtail's JSONField performance
- Full-text search capabilities
- Multi-user concurrency support
- ACID transaction guarantees

### Async ORM Strategy

**Django 4.1+ Native Async ORM** (Preferred):
```python
async def get_post(post_id: int):
    post = await PostTransaction.objects.aget(pk=post_id)
    platforms = [p async for p in post.platforms.all()]
    return post
```

**Wagtail-Specific Operations** (May require `sync_to_async`):
```python
from asgiref.sync import sync_to_async

@sync_to_async
def get_wagtail_page(page_id):
    return Page.objects.get(pk=page_id).specific
```

---

## 3. System Architecture & Adapters

### 3.1 Core Data Models

#### **PostTransaction** (Central Entity)

```python
from django.db import models
from django.utils import timezone
import uuid

class PostTransaction(models.Model):
    """
    Single source of truth for all social media posts.
    Platform-agnostic unified record.

    This model stores the authoritative state of every post,
    regardless of which platforms it's published to.
    """

    # Primary key
    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this post transaction"
    )

    # Wagtail integration
    wagtail_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='post_transactions',
        help_text="Source Wagtail page (if created via CMS)"
    )

    wagtail_page_id = models.IntegerField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Denormalized page ID for quick lookups"
    )

    streamfield_data = models.JSONField(
        default=dict,
        help_text="Snapshot of StreamField data at publish time"
    )

    # Content
    content = models.TextField(
        help_text="Processed content (platform-agnostic text)"
    )

    # Status tracking
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        PUBLISHING = 'PUBLISHING', 'Publishing'
        PUBLISHED = 'PUBLISHED', 'Published'
        PARTIAL = 'PARTIAL', 'Partially Published'  # Some platforms failed
        FAILED = 'FAILED', 'Failed'
        DELETED = 'DELETED', 'Deleted'

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True
    )

    # Platform selection
    platforms = models.JSONField(
        default=list,
        help_text="List of target platforms: ['facebook', 'linkedin', 'line']"
    )

    # Platform-specific post IDs
    facebook_post_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        help_text="Facebook post ID (format: {page_id}_{post_id})"
    )

    linkedin_post_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        help_text="LinkedIn post URN (e.g., urn:li:share:123456)"
    )

    line_message_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        db_index=True,
        help_text="LINE message ID"
    )

    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Actual publish timestamp (when first platform succeeded)"
    )

    scheduled_for = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Scheduled publish time (future)"
    )

    # Retry logic
    retry_count = models.IntegerField(
        default=0,
        help_text="Number of retry attempts"
    )

    last_error = models.TextField(
        null=True,
        blank=True,
        help_text="Last error message (for debugging)"
    )

    # Metadata
    created_by = models.ForeignKey(
        'auth.User',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_posts'
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['scheduled_for', 'status']),
        ]

    def __str__(self):
        return f"Post {self.uuid} - {self.status}"

    @property
    def is_published(self):
        return self.status in [self.Status.PUBLISHED, self.Status.PARTIAL]

    @property
    def platform_urls(self):
        """Return direct URLs to published posts"""
        urls = {}
        if self.facebook_post_id:
            urls['facebook'] = f"https://facebook.com/{self.facebook_post_id}"
        if self.linkedin_post_id:
            # Extract ID from URN if needed
            post_id = self.linkedin_post_id.split(':')[-1]
            urls['linkedin'] = f"https://linkedin.com/feed/update/{self.linkedin_post_id}/"
        if self.line_message_id:
            urls['line'] = f"Message ID: {self.line_message_id}"
        return urls
```

#### **SocialCredential** (Token Management)

```python
from django_cryptography.fields import encrypt

class SocialCredential(models.Model):
    """
    Encrypted storage for OAuth tokens and platform credentials.
    Supports multiple accounts per platform.
    """

    class Platform(models.TextChoices):
        FACEBOOK = 'facebook', 'Facebook'
        LINKEDIN = 'linkedin', 'LinkedIn'
        LINE = 'line', 'LINE'

    # Platform identification
    platform = models.CharField(
        max_length=20,
        choices=Platform.choices
    )

    account_name = models.CharField(
        max_length=200,
        help_text="User-friendly name (e.g., 'Company Facebook Page')"
    )

    # Platform-specific identifiers
    facebook_page_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        unique=True,
        help_text="Facebook Page ID"
    )

    linkedin_org_urn = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        unique=True,
        help_text="LinkedIn organization URN (urn:li:organization:123456)"
    )

    line_channel_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        unique=True,
        help_text="LINE Bot Channel ID"
    )

    # Encrypted tokens (django-cryptography auto-encrypts)
    access_token = encrypt(models.TextField(
        help_text="OAuth access token (encrypted at rest)"
    ))

    refresh_token = encrypt(models.TextField(
        null=True,
        blank=True,
        help_text="OAuth refresh token (if applicable)"
    ))

    # Token lifecycle
    token_expires_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text="Token expiration time (Facebook: 60 days)"
    )

    last_refreshed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last successful token refresh"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this credential is currently in use"
    )

    last_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last time token was verified as valid"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['platform', 'account_name']
        indexes = [
            models.Index(fields=['platform', 'is_active']),
            models.Index(fields=['token_expires_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(platform='facebook', facebook_page_id__isnull=False) |
                    models.Q(platform='linkedin', linkedin_org_urn__isnull=False) |
                    models.Q(platform='line', line_channel_id__isnull=False)
                ),
                name='platform_specific_id_required'
            )
        ]

    def __str__(self):
        return f"{self.get_platform_display()} - {self.account_name}"

    @property
    def is_token_expiring_soon(self):
        """Check if token expires within 10 days"""
        if not self.token_expires_at:
            return False
        threshold = timezone.now() + timezone.timedelta(days=10)
        return self.token_expires_at < threshold
```

#### **PlatformPublishRecord** (Per-Platform Tracking)

```python
class PlatformPublishRecord(models.Model):
    """
    Individual platform publish attempt records.
    Enables granular retry and debugging.
    """

    transaction = models.ForeignKey(
        PostTransaction,
        related_name='platform_records',
        on_delete=models.CASCADE
    )

    platform = models.CharField(
        max_length=20,
        choices=SocialCredential.Platform.choices
    )

    # Platform response
    platform_post_id = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    platform_url = models.URLField(
        null=True,
        blank=True,
        help_text="Direct link to published post"
    )

    # Status tracking
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        UPLOADING = 'UPLOADING', 'Uploading Media'
        PUBLISHING = 'PUBLISHING', 'Publishing'
        PUBLISHED = 'PUBLISHED', 'Published'
        FAILED = 'FAILED', 'Failed'

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # Error handling
    error_message = models.TextField(
        null=True,
        blank=True
    )

    error_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text="Platform-specific error code (e.g., '190' for FB token error)"
    )

    retry_count = models.IntegerField(
        default=0
    )

    # Media tracking (for LinkedIn 3-step upload)
    media_uploaded = models.BooleanField(
        default=False
    )

    media_asset_urn = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="LinkedIn asset URN after upload"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['transaction', 'platform']),
            models.Index(fields=['status', '-created_at']),
        ]
        unique_together = [['transaction', 'platform']]

    def __str__(self):
        return f"{self.platform} - {self.transaction.uuid} - {self.status}"
```

#### **LineAudience** (LINE-Specific User Management)

```python
class LineAudience(models.Model):
    """
    Stores LINE user IDs for targeting.
    Built from webhook interactions.
    """

    line_user_id = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="LINE user ID (e.g., U4af4980629...)"
    )

    display_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text="User's display name (from LINE profile)"
    )

    profile_picture_url = models.URLField(
        null=True,
        blank=True,
        help_text="User's profile picture URL"
    )

    # Segmentation
    tags = models.JSONField(
        default=list,
        help_text="User tags for segmentation (e.g., ['vip', 'newsletter'])"
    )

    # Interaction history
    first_interaction = models.DateTimeField(
        auto_now_add=True,
        help_text="When user first interacted with bot"
    )

    last_interaction = models.DateTimeField(
        auto_now=True,
        help_text="Last interaction timestamp"
    )

    message_count = models.IntegerField(
        default=0,
        help_text="Total messages received from this user"
    )

    # Status
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether user is still following the bot"
    )

    is_blocked = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether user has blocked the bot"
    )

    opted_out_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When user opted out of messages"
    )

    # Metadata
    custom_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional custom data (e.g., preferences, purchase history)"
    )

    class Meta:
        ordering = ['-last_interaction']
        indexes = [
            models.Index(fields=['is_active', '-last_interaction']),
            models.Index(fields=['tags']),
        ]

    def __str__(self):
        name = self.display_name or self.line_user_id[:10]
        return f"{name} ({'active' if self.is_active else 'inactive'})"

    def add_tag(self, tag: str):
        """Add a tag to this user"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.save(update_fields=['tags'])

    def remove_tag(self, tag: str):
        """Remove a tag from this user"""
        if tag in self.tags:
            self.tags.remove(tag)
            self.save(update_fields=['tags'])

    @classmethod
    def get_by_tags(cls, tags: list[str], all_tags: bool = False):
        """
        Get users matching tags.

        Args:
            tags: List of tags to match
            all_tags: If True, user must have ALL tags. If False, ANY tag.
        """
        if all_tags:
            # User must have all specified tags
            queryset = cls.objects.filter(is_active=True)
            for tag in tags:
                queryset = queryset.filter(tags__contains=[tag])
            return queryset
        else:
            # User has any of the specified tags
            from django.db.models import Q
            query = Q()
            for tag in tags:
                query |= Q(tags__contains=[tag])
            return cls.objects.filter(query, is_active=True)
```

---

### 3.2 Wagtail Serialization Strategy

**Challenge**: Wagtail Page objects cannot be directly returned from Django Ninja endpoints. We need to convert Page → Pydantic Schema → JSON.

#### **Approach: Pydantic Schema Conversion**

```python
from ninja import Schema, ModelSchema, Field
from typing import Literal, Optional, List
from wagtail.models import Page
from wagtail.rich_text import expand_db_html

# Base schema for all page types
class BasePageSchema(Schema):
    """
    Base schema for Wagtail pages.
    Provides common fields for all page types.
    """
    id: int
    title: str
    slug: str
    url: str = Field(None, alias="get_url")
    content_type: str

    @staticmethod
    def resolve_content_type(page: Page) -> str:
        """Get page type name for discriminator"""
        return page.specific_class._meta.model_name

    @staticmethod
    def resolve_url(page: Page) -> str:
        """Get full URL for page"""
        return page.full_url or page.get_url()

# Specific page schemas with content type discriminator
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

    scheduled_publish_time: Optional[str] = None

    @staticmethod
    def resolve_headline(page) -> str:
        """Extract headline from StreamField"""
        for block in page.content:
            if block.block_type == 'post':
                return block.value['headline']
        return ""

    @staticmethod
    def resolve_body_html(page) -> str:
        """Convert RichTextBlock to HTML"""
        for block in page.content:
            if block.block_type == 'post':
                return expand_db_html(block.value['body'])
        return ""

    @staticmethod
    def resolve_body_text(page) -> str:
        """Convert RichTextBlock to plain text"""
        from django.utils.html import strip_tags
        html = SocialPostPageSchema.resolve_body_html(page)
        return strip_tags(html)

    @staticmethod
    def resolve_image_url(page) -> Optional[str]:
        """Extract image URL from StreamField"""
        for block in page.content:
            if block.block_type == 'post':
                image = block.value.get('image')
                if image:
                    return image.file.url
        return None

# API endpoint using schema
from ninja import NinjaAPI
from asgiref.sync import sync_to_async

api = NinjaAPI()

@api.get("/pages/{page_id}/", response=SocialPostPageSchema)
async def get_page(request, page_id: int):
    """
    Get page with automatic Pydantic serialization.
    """
    # Fetch page asynchronously
    page = await sync_to_async(lambda: Page.objects.get(id=page_id).specific)()

    # Django Ninja automatically serializes using schema resolvers
    return page

@api.get("/pages/", response=List[BasePageSchema])
async def list_pages(request):
    """
    List all pages with polymorphic serialization.
    """
    pages = await sync_to_async(list)(Page.objects.live().specific())
    return pages
```

#### **StreamField Processing Utility**

```python
from wagtail.fields import StreamField
from typing import Dict, Any

class StreamFieldSerializer:
    """
    Utility class for converting StreamField to various formats.
    """

    @staticmethod
    def to_dict(streamfield: StreamField) -> List[Dict[str, Any]]:
        """
        Convert StreamField to list of dicts.

        Returns:
            [
                {"type": "heading", "value": "My Heading"},
                {"type": "paragraph", "value": "<p>Content</p>"},
                ...
            ]
        """
        return [
            {
                "type": block.block_type,
                "value": block.value,
                "id": str(block.id)
            }
            for block in streamfield
        ]

    @staticmethod
    def to_text(streamfield: StreamField) -> str:
        """
        Convert StreamField to plain text (for social media).
        """
        from django.utils.html import strip_tags
        from wagtail.rich_text import expand_db_html

        parts = []
        for block in streamfield:
            if block.block_type == 'post':
                # Headline
                if 'headline' in block.value:
                    parts.append(block.value['headline'])

                # Body (strip HTML)
                if 'body' in block.value:
                    html = expand_db_html(block.value['body'])
                    text = strip_tags(html)
                    parts.append(text)

                # CTA
                if block.value.get('cta_text') and block.value.get('cta_url'):
                    parts.append(f"{block.value['cta_text']}: {block.value['cta_url']}")

        return '\n\n'.join(parts)

    @staticmethod
    def extract_media(streamfield: StreamField) -> Optional[bytes]:
        """
        Extract first image from StreamField as bytes.
        """
        for block in streamfield:
            if block.block_type == 'post':
                image = block.value.get('image')
                if image:
                    return image.file.read()
        return None
```

#### **Why This Approach?**

1. **Type Safety**: Pydantic validates all fields automatically
2. **Auto-Documentation**: OpenAPI schema generated automatically
3. **Separation of Concerns**: Wagtail stores data, Pydantic defines API contract
4. **Frontend Integration**: TypeScript types can be generated from schemas
5. **Flexibility**: Different schemas for different API consumers (web, mobile, etc.)

---

### 3.3 Platform Adapters

#### **FacebookAdapter**

```python
class FacebookAdapter:
    """
    Facebook Graph API integration.

    API Limitations:
    - Token expiry: 60 days (long-lived)
    - Rate limit: ~2,000 requests/sec (app-level)
    - Duplicate posts: Error 506 if consecutive identical content
    - Image upload: Direct upload with POST to /photos endpoint
    """

    GRAPH_API_BASE = "https://graph.facebook.com/v24.0"

    async def publish_post(self, page_id: str, content: str, image: bytes = None):
        """
        Publishes to Page feed with optional image.
        Uses read-after-write pattern for immediate confirmation.
        """
        if image:
            endpoint = f"{self.GRAPH_API_BASE}/{page_id}/photos"
            files = {'source': image}
            data = {
                'message': content,
                'fields': 'id,post_id,created_time'
            }
        else:
            endpoint = f"{self.GRAPH_API_BASE}/{page_id}/feed"
            data = {
                'message': content,
                'fields': 'id,created_time,message'
            }

        # Implementation with error handling...
        # Handle error 190 (expired token)
        # Handle error 506 (duplicate post)
        # Handle rate limiting (429)

    async def refresh_token(self, short_lived_token: str) -> dict:
        """
        Exchange short-lived token (1-2 hrs) for long-lived (60 days).

        Endpoint: GET /oauth/access_token
        """
        params = {
            'grant_type': 'fb_exchange_token',
            'client_id': settings.FACEBOOK_APP_ID,
            'client_secret': settings.FACEBOOK_APP_SECRET,
            'fb_exchange_token': short_lived_token
        }
        # Returns: {access_token, expires_in}
```

---

#### **LinkedInAdapter** (Updated to /rest/posts API)

```python
class LinkedInAdapter:
    """
    LinkedIn Posts API integration (2025 - latest version).

    API Updates:
    - ✅ NEW: /rest/posts endpoint (replaces /v2/ugcPosts)
    - ✅ Simpler image upload flow
    - ⚠️ Still requires SYNCHRONOUS_UPLOAD for reliability

    API Limitations:
    - Image size: <36,152,320 pixels (~6000x6000)
    - Formats: JPG, GIF (max 250 frames), PNG
    - Role required: ADMINISTRATOR or DIRECT_SPONSORED_CONTENT_POSTER
    """

    REST_API_BASE = "https://api.linkedin.com/rest"

    async def publish_post(self, org_urn: str, content: str, image: bytes = None):
        """
        Full publish workflow using /rest/posts API.

        Steps:
        1. If image: Upload via Images API (simplified 2-step)
        2. Create Post using /rest/posts
        3. Return post ID and URL
        """
        image_id = None
        if image:
            image_id = await self._upload_image(org_urn, image)

        post_id = await self._create_post(org_urn, content, image_id)
        return post_id

    async def _upload_image(self, org_urn: str, image_data: bytes) -> str:
        """
        NEW Simplified image upload (Images API).

        STEP 1: Initialize Upload
        POST /rest/images?action=initializeUpload
        {
            "initializeUploadRequest": {
                "owner": "urn:li:organization:123456"
            }
        }
        Returns: {uploadUrl, image: "urn:li:image:..."}

        STEP 2: Upload Binary
        PUT {uploadUrl}
        [Binary data]

        Returns: image URN
        """
        # Step 1: Initialize
        init_response = await self.client.post(
            f"{self.REST_API_BASE}/images?action=initializeUpload",
            json={
                "initializeUploadRequest": {
                    "owner": org_urn
                }
            }
        )

        upload_url = init_response['value']['uploadUrl']
        image_urn = init_response['value']['image']

        # Step 2: Upload
        await self.client.put(
            upload_url,
            data=image_data,
            headers={'Content-Type': 'image/jpeg'}
        )

        return image_urn

    async def _create_post(self, org_urn: str, content: str, image_id: str = None):
        """
        Create post using NEW /rest/posts endpoint.

        POST /rest/posts
        {
            "author": "urn:li:organization:123456",
            "commentary": "Your post text here",
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": []
            },
            "content": {
                "media": {
                    "title": "Image title",
                    "id": "urn:li:image:..."
                }
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": false
        }
        """
        payload = {
            "author": org_urn,
            "commentary": content,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED"
            },
            "lifecycleState": "PUBLISHED"
        }

        # Add image if provided
        if image_id:
            payload["content"] = {
                "media": {
                    "title": "Post Image",
                    "id": image_id
                }
            }

        response = await self.client.post(
            f"{self.REST_API_BASE}/posts",
            json=payload
        )

        post_id = response['id']
        return post_id
```

**LinkedIn API Migration Notes**:
- ✅ **Old API**: `/v2/ugcPosts` (still works but deprecated)
- ✅ **New API**: `/rest/posts` (recommended for 2025+)
- **Image Upload**: Now uses `/rest/images` (simpler than old 3-step Vector Assets API)
- **Benefits**: Cleaner API, better documentation, forward compatibility

---

#### **LineAdapter**

```python
class LineAdapter:
    """
    LINE Messaging API integration.

    API Limitations & Critical Changes:
    - Push message: 2,000 requests/sec ✅
    - Multicast: 200 requests/sec ⚠️ (CHANGED April 23, 2025 - 90% reduction!)
    - Broadcast: 60 requests/hour
    - Messages per request: Max 5 messages
    - Custom aggregation: 1,000 unique unit names/month
    """

    MESSAGING_API_BASE = "https://api.line.me/v2/bot"

    async def send_push_message(self, user_id: str, content: str):
        """
        Send message to single user (RECOMMENDED over multicast).
        Rate limit: 2,000 req/sec (stable)
        """
        payload = {
            "to": user_id,
            "messages": [
                {"type": "text", "text": content}
            ]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.MESSAGING_API_BASE}/message/push",
                json=payload,
                headers={
                    'Authorization': f'Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}',
                    'Content-Type': 'application/json'
                }
            )
            return response.json()

    async def send_multicast_message(self, user_ids: list[str], content: str):
        """
        Send to multiple users (max 500 per request).

        ⚠️ WARNING: Rate limit is 200 req/sec (REDUCED from 2,000 in April 2025).
        Only use for true broadcast scenarios.
        """
        # If single user, use push instead
        if len(user_ids) == 1:
            return await self.send_push_message(user_ids[0], content)

        # Batch into chunks of 500
        for chunk in self._chunks(user_ids, 500):
            payload = {
                "to": chunk,
                "messages": [{"type": "text", "text": content}]
            }
            # Apply rate limiting...
```

---

### 3.4 Adapter Factory Pattern

```python
from typing import Protocol

class SocialMediaAdapter(Protocol):
    """Protocol defining adapter interface"""
    async def publish_post(self, account_id: str, content: str, media: bytes = None) -> str:
        """Returns platform post ID"""
        ...

class AdapterFactory:
    """Factory for creating platform-specific adapters"""

    @staticmethod
    def get_adapter(platform: str) -> SocialMediaAdapter:
        adapters = {
            'facebook': FacebookAdapter(),
            'linkedin': LinkedInAdapter(),
            'line': LineAdapter(),
        }
        return adapters[platform]
```

---

## 4. Feature Specifications

### 4.1 Headless Content Management (Wagtail)

**StreamField Configuration**:

```python
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.blocks import CharBlock, RichTextBlock, ImageChooserBlock, StructBlock, URLBlock

class SocialPostBlock(StructBlock):
    """Custom block for social media posts"""
    headline = CharBlock(max_length=280, help_text="Post headline (max 280 chars)")
    body = RichTextBlock(help_text="Main post content")
    image = ImageChooserBlock(required=False, help_text="Optional post image")
    cta_text = CharBlock(max_length=50, required=False, help_text="Call-to-action text")
    cta_url = URLBlock(required=False, help_text="Call-to-action URL")

    class Meta:
        icon = 'doc-full'
        label = 'Social Post'

class SocialPostPage(Page):
    """Wagtail page model for social posts"""

    content = StreamField([
        ('post', SocialPostBlock()),
    ], use_json_field=True)

    # Platform selection
    publish_to_facebook = models.BooleanField(default=True)
    publish_to_linkedin = models.BooleanField(default=True)
    publish_to_line = models.BooleanField(default=False)

    # Scheduling
    scheduled_publish_time = models.DateTimeField(null=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('content'),
        MultiFieldPanel([
            FieldPanel('publish_to_facebook'),
            FieldPanel('publish_to_linkedin'),
            FieldPanel('publish_to_line'),
        ], heading="Publishing Platforms"),
        FieldPanel('scheduled_publish_time'),
    ]

    def save(self, *args, **kwargs):
        """Override to trigger publishing workflow"""
        is_publishing = self.live and not self._state.adding
        super().save(*args, **kwargs)

        if is_publishing:
            from .tasks import publish_to_platforms
            platforms = []
            if self.publish_to_facebook:
                platforms.append('facebook')
            if self.publish_to_linkedin:
                platforms.append('linkedin')
            if self.publish_to_line:
                platforms.append('line')

            publish_to_platforms.delay(self.id, platforms)
```

---

### 4.2 Django Ninja API Gateway

```python
from ninja import NinjaAPI, Schema
from typing import List, Optional
from datetime import datetime

api = NinjaAPI(title="Social Media Hub API", version="1.0.0")

# Schemas
class PostStatusResponse(Schema):
    uuid: str
    status: str
    content: str
    published_at: Optional[datetime]
    facebook_url: Optional[str]
    linkedin_url: Optional[str]
    line_message_id: Optional[str]

@api.get("/posts/{uuid}", response=PostStatusResponse)
async def get_post_status(request, uuid: str):
    """Get current status of a post across all platforms"""
    post = await PostTransaction.objects.aget(uuid=uuid)
    return {
        "uuid": str(post.uuid),
        "status": post.status,
        "content": post.content,
        "published_at": post.published_at,
        "facebook_url": post.platform_urls.get('facebook'),
        "linkedin_url": post.platform_urls.get('linkedin'),
        "line_message_id": post.line_message_id,
    }
```

---

### 4.3 Async Task Processing (Celery)

```python
from celery import shared_task
import asyncio

@shared_task(bind=True, max_retries=3)
def publish_to_platforms(self, page_id: int, platforms: list[str]):
    """
    Async task to publish Wagtail page to selected platforms.
    """
    from social.models import SocialPostPage, PostTransaction
    from social.adapters import AdapterFactory
    from social.utils import StreamFieldSerializer

    # Get page
    page = SocialPostPage.objects.get(id=page_id)

    # Create transaction
    post = PostTransaction.objects.create(
        wagtail_page=page,
        wagtail_page_id=page.id,
        content=StreamFieldSerializer.to_text(page.content),
        streamfield_data=StreamFieldSerializer.to_dict(page.content),
        platforms=platforms,
        status=PostTransaction.Status.PUBLISHING,
    )

    # Extract media
    image = StreamFieldSerializer.extract_media(page.content)

    # Publish to each platform
    for platform in platforms:
        try:
            adapter = AdapterFactory.get_adapter(platform)
            credential = SocialCredential.objects.get(platform=platform, is_active=True)

            # Get account ID
            account_id = (
                credential.facebook_page_id or
                credential.linkedin_org_urn or
                credential.line_channel_id
            )

            # Publish
            post_id = asyncio.run(
                adapter.publish_post(account_id, post.content, image)
            )

            # Update post
            setattr(post, f'{platform}_post_id', post_id)

            # Create success record
            PlatformPublishRecord.objects.create(
                transaction=post,
                platform=platform,
                platform_post_id=post_id,
                status='PUBLISHED',
                published_at=timezone.now(),
            )

        except Exception as e:
            # Create failure record
            PlatformPublishRecord.objects.create(
                transaction=post,
                platform=platform,
                status='FAILED',
                error_message=str(e),
            )

    # Update overall status
    records = post.platform_records.all()
    if all(r.status == 'PUBLISHED' for r in records):
        post.status = PostTransaction.Status.PUBLISHED
    elif any(r.status == 'PUBLISHED' for r in records):
        post.status = PostTransaction.Status.PARTIAL
    else:
        post.status = PostTransaction.Status.FAILED

    post.save()
```

---

## 5. Implementation Roadmap

### Phase 1: Project Initialization (Week 1)

**Deliverables**: Running Django + Wagtail + Ninja environment

**Tasks**:
- [ ] Create Django 5 project
- [ ] Install Wagtail in headless mode
- [ ] Install Django Ninja and configure API
- [ ] Set up Celery + Redis
- [ ] Configure SQLite for development ✅
- [ ] Create base project structure

**Environment Setup**:
```bash
# Create project
django-admin startproject config .
python manage.py startapp social

# Install dependencies
pip install django==5.0 wagtail django-ninja celery redis django-cryptography

# Development uses SQLite (zero config)
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

**Success Criteria**:
- ✅ Django admin at `/admin`
- ✅ Wagtail admin at `/cms`
- ✅ API docs at `/api/docs`
- ✅ Celery worker running

---

### Phase 2: Core Models & Wagtail Integration (Week 2)

**Deliverables**: Database schema + CMS interface

**Tasks**:
- [ ] Create all core models (PostTransaction, SocialCredential, etc.)
- [ ] Run migrations
- [ ] Build SocialPostPage in Wagtail
- [ ] Implement Pydantic schemas
- [ ] Create StreamField converters

**Success Criteria**:
- ✅ Can create posts in Wagtail CMS
- ✅ StreamField saves correctly
- ✅ API returns Pydantic-serialized pages

---

### Phase 3: LINE Integration (Week 3-4)

**Why LINE First?**
- Most complex local DB interaction (LineAudience)
- Critical rate limit change (April 2025)
- Webhook foundation for all platforms

**Tasks**:
- [ ] Build LineAdapter
- [ ] Implement webhook endpoint
- [ ] Create rate limiter (200 req/sec for multicast)
- [ ] Build LineAudience management

**Success Criteria**:
- ✅ Can publish to LINE
- ✅ Webhook receives events
- ✅ Rate limiting prevents 429 errors

---

### Phase 4: Facebook & LinkedIn Adapters (Week 5-6)

**Phase 4A: Facebook (Week 5)**
- [ ] Build FacebookAdapter
- [ ] Implement token refresh (60-day cycle)
- [ ] Handle error codes (190, 506, 429)

**Phase 4B: LinkedIn (Week 6)**
- [ ] Build LinkedInAdapter with /rest/posts API ✅
- [ ] Implement new Images API upload
- [ ] Test organization permissions

**Success Criteria**:
- ✅ Text + image posts to both platforms
- ✅ Token refresh works automatically
- ✅ Posts visible on platforms

---

### Phase 5: Unified Publishing & Dashboard (Week 7-8)

**Tasks**:
- [ ] Integrate all adapters
- [ ] Build status dashboard
- [ ] Implement scheduled publishing
- [ ] Add retry logic

**Success Criteria**:
- ✅ Single post publishes to all 3 platforms
- ✅ Failed platforms can be retried
- ✅ Dashboard shows real-time status

---

## 6. Critical API Limitations Summary

### Facebook Graph API
| Limitation | Value | Mitigation Strategy |
|------------|-------|---------------------|
| Token Expiry | 60 days | Auto-refresh 10 days before expiry via Celery |
| Rate Limit | ~2,000 req/sec | Use Celery queue to throttle requests |
| Duplicate Posts | Error 506 | Add timestamp or unique marker to content |
| Image Upload | Direct to /photos | Validate size/format before upload |
| Permissions | `pages_manage_posts` required | Validate during credential setup |

### LinkedIn Posts API (NEW 2025)
| Limitation | Value | Mitigation Strategy |
|------------|-------|---------------------|
| API Version | ✅ `/rest/posts` (new) | Use latest API, not deprecated `/v2/ugcPosts` |
| Image Size | <36,152,320 pixels | Validate dimensions before upload |
| Image Upload | `/rest/images` API | Simplified 2-step process |
| Role Required | ADMINISTRATOR or POSTER | Verify during credential setup |
| Author URN | Must match owner | Store org URN with credential, validate |

### LINE Messaging API
| Limitation | Value | Mitigation Strategy |
|------------|-------|---------------------|
| Multicast Rate | **200 req/sec** ⚠️ (April 2025) | Use push messages for single users instead |
| Push Rate | 2,000 req/sec ✅ | Preferred method (10x faster) |
| Messages/Request | Max 5 messages | Batch appropriately |
| Multicast Recipients | Max 500 per request | Split large audiences |
| Webhook Security | HMAC-SHA256 required | Always verify signature |

---

## 7. Security & Best Practices

### Token Encryption
```python
from django_cryptography.fields import encrypt

class SocialCredential(models.Model):
    access_token = encrypt(models.TextField())  # Auto-encrypted

    # Usage: automatic decryption
    token = credential.access_token  # Returns decrypted value
```

### Webhook Security (LINE)
```python
import hmac, hashlib, base64

def verify_line_signature(body: bytes, signature: str) -> bool:
    secret = settings.LINE_CHANNEL_SECRET.encode()
    digest = hmac.new(secret, body, hashlib.sha256).digest()
    expected = base64.b64encode(digest).decode()
    return hmac.compare_digest(signature, expected)
```

### Environment Variables
```env
# .env
SECRET_KEY=your-secret-key
DEBUG=True

# Development: SQLite (no config needed)
# Production: PostgreSQL
DATABASE_URL=postgresql://user:pass@localhost/socialhub

REDIS_URL=redis://localhost:6379/0

# Platform credentials
FACEBOOK_APP_ID=123456789
FACEBOOK_APP_SECRET=your-secret
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-secret
LINE_CHANNEL_SECRET=your-secret
LINE_CHANNEL_ACCESS_TOKEN=your-token
```

---

## 8. Testing Strategy

### Unit Tests
```python
@pytest.mark.asyncio
async def test_linkedin_publish(mocker):
    """Test LinkedIn adapter with new /rest/posts API"""
    mock_post = mocker.patch('httpx.AsyncClient.post')
    mock_post.return_value.json.return_value = {'id': 'urn:li:share:123'}

    adapter = LinkedInAdapter()
    result = await adapter.publish_post('urn:li:organization:123', 'Test')

    # Verify new API endpoint used
    mock_post.assert_called_with(
        'https://api.linkedin.com/rest/posts',
        json=mocker.ANY
    )
```

---

## 9. Monitoring & Observability

### Structured Logging
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "post_published",
    transaction_uuid=str(post.uuid),
    platform="linkedin",
    api_version="rest_posts",  # Track API version
    post_id=post.linkedin_post_id,
    duration_ms=duration,
)
```

---

## 10. Deployment

### Production Checklist
- [ ] Switch from SQLite to PostgreSQL ⚠️
- [ ] Configure Redis persistence
- [ ] Set up Celery workers (min 2)
- [ ] Configure S3 for media
- [ ] SSL/TLS for webhooks
- [ ] Environment variables in secrets manager

### Database Migration (Dev → Prod)
```bash
# Development (SQLite)
python manage.py migrate

# Production (PostgreSQL)
# Update settings.py:
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL')
    )
}

# Run migrations
python manage.py migrate --database=default
```

---

## 11. Platform API Quick Reference

### Facebook Graph API
```http
# Publish text post
POST https://graph.facebook.com/v24.0/{PAGE_ID}/feed
message=Your content&access_token={TOKEN}

# Publish photo
POST https://graph.facebook.com/v24.0/{PAGE_ID}/photos
message=Caption&source={IMAGE}&access_token={TOKEN}

# Refresh token
GET https://graph.facebook.com/v24.0/oauth/access_token?
    grant_type=fb_exchange_token&
    client_id={APP_ID}&
    client_secret={APP_SECRET}&
    fb_exchange_token={SHORT_TOKEN}
```

---

### LinkedIn Posts API (NEW 2025) ✅

```http
# Initialize image upload
POST https://api.linkedin.com/rest/images?action=initializeUpload
Authorization: Bearer {TOKEN}
Content-Type: application/json

{
  "initializeUploadRequest": {
    "owner": "urn:li:organization:123456"
  }
}

# Response:
{
  "value": {
    "uploadUrl": "https://...",
    "image": "urn:li:image:..."
  }
}

# Upload image
PUT {uploadUrl}
[Binary data]

# Create post with image
POST https://api.linkedin.com/rest/posts
Authorization: Bearer {TOKEN}

{
  "author": "urn:li:organization:123456",
  "commentary": "Your post text",
  "visibility": "PUBLIC",
  "distribution": {
    "feedDistribution": "MAIN_FEED"
  },
  "content": {
    "media": {
      "title": "Image title",
      "id": "urn:li:image:..."
    }
  },
  "lifecycleState": "PUBLISHED"
}
```

---

### LINE Messaging API

```http
# Push message (single user)
POST https://api.line.me/v2/bot/message/push
Authorization: Bearer {TOKEN}

{
  "to": "U4af4980629...",
  "messages": [{"type": "text", "text": "Hello"}]
}

# Multicast (multiple users, max 500)
POST https://api.line.me/v2/bot/message/multicast

{
  "to": ["U123...", "U456..."],
  "messages": [{"type": "text", "text": "Broadcast"}]
}

# Unsend message
POST https://api.line.me/v2/bot/message/{MESSAGE_ID}/unsend
Authorization: Bearer {TOKEN}
```

---

## 12. Next Steps

### Immediate Actions (Week 1)
1. **Review & Approve** this document
2. **Repository Setup**:
   ```bash
   git init
   git remote add origin <repo-url>
   ```
3. **Development Environment**:
   - Install Python 3.11+, Redis
   - SQLite comes with Python ✅
   - Create virtualenv
4. **CI/CD Pipeline**: GitHub Actions

### Phase 1 Kickoff
- Set up Django with SQLite ✅
- Install Wagtail + Django Ninja
- Create initial models
- Write first tests

### Open Questions
- [ ] Frontend framework choice?
- [ ] Hosting platform (AWS, Heroku, Railway)?
- [ ] Multi-tenancy support?
- [ ] Content approval workflow?

---

## 13. Key Takeaways

### Critical Fixes Applied ✅

1. **Complete Data Models**: All field definitions added with proper relationships
2. **LinkedIn API Updated**: Migrated from `/v2/ugcPosts` to `/rest/posts` (2025 standard)
3. **SQLite for Dev**: Explicitly emphasized for rapid development
4. **Fixed Numbering**: Proper sequential section ordering
5. **Wagtail Serialization**: Added comprehensive Pydantic schema conversion guide

### API Insights

- **Facebook**: 60-day token refresh mandatory
- **LinkedIn**: New `/rest/posts` API simplifies publishing
- **LINE**: April 2025 multicast rate limit drop requires strategy change

### Architectural Decisions

- **Database-first**: Local DB is single source of truth
- **Pydantic serialization**: Clean separation between Wagtail storage and API contracts
- **Adapter pattern**: Platform-specific logic isolated
- **SQLite → PostgreSQL**: Clear migration path from dev to prod

---

**Document Version**: 2.0 (Corrected)
**Last Updated**: 2026-01-27
**Author**: Development Team
**Status**: ✅ Ready for Implementation

**Critical Changes from v1.0**:
- ✅ Added complete model definitions (3.1)
- ✅ Updated LinkedIn to /rest/posts API
- ✅ Emphasized SQLite for development
- ✅ Fixed section numbering
- ✅ Added Wagtail serialization strategy (3.2)
