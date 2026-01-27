"""
Social Media Hub - Core Models

This module contains the database-first models that serve as the
single source of truth for all social media operations.
"""

from django.db import models
from django.utils import timezone
import uuid

# TODO: Implement proper token encryption for production
# django-cryptography has compatibility issues with Django 5.0
# Consider using environment-based secrets manager or django-fernet-fields


class PostTransaction(models.Model):
    """
    Single source of truth for all social media posts.
    Platform-agnostic unified record.

    This model stores the authoritative state of every post,
    regardless of which platforms it's published to.
    """

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SCHEDULED = 'SCHEDULED', 'Scheduled'
        PUBLISHING = 'PUBLISHING', 'Publishing'
        PUBLISHED = 'PUBLISHED', 'Published'
        PARTIAL = 'PARTIAL', 'Partially Published'  # Some platforms failed
        FAILED = 'FAILED', 'Failed'
        DELETED = 'DELETED', 'Deleted'

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
        help_text="Source Wagtail page (if created via CMS)",
        db_index=True  # Auto-creates wagtail_page_id with index
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
        """Check if post is published (fully or partially)."""
        return self.status in [self.Status.PUBLISHED, self.Status.PARTIAL]

    @property
    def platform_urls(self):
        """Return direct URLs to published posts."""
        urls = {}
        if self.facebook_post_id:
            urls['facebook'] = f"https://facebook.com/{self.facebook_post_id}"
        if self.linkedin_post_id:
            urls['linkedin'] = f"https://linkedin.com/feed/update/{self.linkedin_post_id}/"
        if self.line_message_id:
            urls['line'] = f"Message ID: {self.line_message_id}"
        return urls


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

    # Tokens (TODO: Add encryption for production)
    # For Phase 2 development, using TextField
    # Production should use proper secrets management
    access_token = models.TextField(
        help_text="OAuth access token (TODO: encrypt at rest)"
    )

    refresh_token = models.TextField(
        null=True,
        blank=True,
        help_text="OAuth refresh token (if applicable)"
    )

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
        """Check if token expires within 10 days."""
        if not self.token_expires_at:
            return False
        threshold = timezone.now() + timezone.timedelta(days=10)
        return self.token_expires_at < threshold


class PlatformPublishRecord(models.Model):
    """
    Individual platform publish attempt records.
    Enables granular retry and debugging.
    """

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        UPLOADING = 'UPLOADING', 'Uploading Media'
        PUBLISHING = 'PUBLISHING', 'Publishing'
        PUBLISHED = 'PUBLISHED', 'Published'
        FAILED = 'FAILED', 'Failed'

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
        """Add a tag to this user."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.save(update_fields=['tags'])

    def remove_tag(self, tag: str):
        """Remove a tag from this user."""
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
        
        Note: This method uses Python filtering for SQLite compatibility.
        For production with PostgreSQL, this could be optimized with
        JSONField contains lookups.
        """
        # Fetch all active users and filter in Python (SQLite compatible)
        active_users = cls.objects.filter(is_active=True)
        
        if all_tags:
            # User must have all specified tags
            return [
                user for user in active_users
                if all(tag in user.tags for tag in tags)
            ]
        else:
            # User has any of the specified tags
            return [
                user for user in active_users
                if any(tag in user.tags for tag in tags)
            ]
