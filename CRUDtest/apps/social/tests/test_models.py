"""
Tests for Social Media Hub models.
"""

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from apps.social.models import (
    PostTransaction,
    SocialCredential,
    PlatformPublishRecord,
    LineAudience
)

User = get_user_model()


@pytest.mark.django_db
class TestPostTransaction:
    """Tests for PostTransaction model."""

    def test_create_post_transaction(self):
        """Test creating a basic post transaction."""
        post = PostTransaction.objects.create(
            content="Test post content",
            platforms=['facebook', 'linkedin']
        )
        
        assert post.uuid is not None
        assert post.content == "Test post content"
        assert post.platforms == ['facebook', 'linkedin']
        assert post.status == PostTransaction.Status.DRAFT
        assert post.retry_count == 0

    def test_post_transaction_with_user(self):
        """Test creating post with user association."""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        post = PostTransaction.objects.create(
            content="Test content",
            platforms=['facebook'],
            created_by=user
        )
        
        assert post.created_by == user

    def test_is_published_property(self):
        """Test is_published property."""
        post = PostTransaction.objects.create(
            content="Test",
            platforms=['facebook']
        )
        
        # Draft should not be published
        assert not post.is_published
        
        # Published status
        post.status = PostTransaction.Status.PUBLISHED
        post.save()
        assert post.is_published
        
        # Partial status
        post.status = PostTransaction.Status.PARTIAL
        post.save()
        assert post.is_published
        
        # Failed status
        post.status = PostTransaction.Status.FAILED
        post.save()
        assert not post.is_published

    def test_platform_urls_property(self):
        """Test platform_urls property."""
        post = PostTransaction.objects.create(
            content="Test",
            platforms=['facebook', 'linkedin', 'line'],
            facebook_post_id='123456_789012',
            linkedin_post_id='urn:li:share:123456',
            line_message_id='msg_123'
        )
        
        urls = post.platform_urls
        assert 'facebook' in urls
        assert 'linkedin' in urls
        assert 'line' in urls
        assert '123456_789012' in urls['facebook']
        assert 'urn:li:share:123456' in urls['linkedin']
        assert 'msg_123' in urls['line']

    def test_scheduled_post(self):
        """Test scheduled post creation."""
        future_time = timezone.now() + timedelta(days=1)
        post = PostTransaction.objects.create(
            content="Scheduled post",
            platforms=['facebook'],
            status=PostTransaction.Status.SCHEDULED,
            scheduled_for=future_time
        )
        
        assert post.scheduled_for is not None
        assert post.scheduled_for > timezone.now()


@pytest.mark.django_db
class TestSocialCredential:
    """Tests for SocialCredential model."""

    def test_create_facebook_credential(self):
        """Test creating Facebook credential."""
        cred = SocialCredential.objects.create(
            platform=SocialCredential.Platform.FACEBOOK,
            account_name="Test Facebook Page",
            facebook_page_id="123456789",
            access_token="test_token_123"
        )
        
        assert cred.platform == 'facebook'
        assert cred.facebook_page_id == "123456789"
        assert cred.is_active is True

    def test_create_linkedin_credential(self):
        """Test creating LinkedIn credential."""
        cred = SocialCredential.objects.create(
            platform=SocialCredential.Platform.LINKEDIN,
            account_name="Test Company",
            linkedin_org_urn="urn:li:organization:123456",
            access_token="test_token_456"
        )
        
        assert cred.platform == 'linkedin'
        assert cred.linkedin_org_urn == "urn:li:organization:123456"

    def test_create_line_credential(self):
        """Test creating LINE credential."""
        cred = SocialCredential.objects.create(
            platform=SocialCredential.Platform.LINE,
            account_name="Test LINE Bot",
            line_channel_id="1234567890",
            access_token="test_token_789"
        )
        
        assert cred.platform == 'line'
        assert cred.line_channel_id == "1234567890"

    def test_token_expiring_soon(self):
        """Test is_token_expiring_soon property."""
        # Token expires in 5 days (should be expiring soon)
        cred1 = SocialCredential.objects.create(
            platform=SocialCredential.Platform.FACEBOOK,
            account_name="Test",
            facebook_page_id="123",
            access_token="token",
            token_expires_at=timezone.now() + timedelta(days=5)
        )
        assert cred1.is_token_expiring_soon
        
        # Token expires in 15 days (not expiring soon)
        cred2 = SocialCredential.objects.create(
            platform=SocialCredential.Platform.FACEBOOK,
            account_name="Test2",
            facebook_page_id="456",
            access_token="token",
            token_expires_at=timezone.now() + timedelta(days=15)
        )
        assert not cred2.is_token_expiring_soon

    def test_str_representation(self):
        """Test string representation."""
        cred = SocialCredential.objects.create(
            platform=SocialCredential.Platform.FACEBOOK,
            account_name="My Facebook Page",
            facebook_page_id="123",
            access_token="token"
        )
        
        assert "Facebook" in str(cred)
        assert "My Facebook Page" in str(cred)


@pytest.mark.django_db
class TestPlatformPublishRecord:
    """Tests for PlatformPublishRecord model."""

    def test_create_publish_record(self):
        """Test creating a platform publish record."""
        post = PostTransaction.objects.create(
            content="Test",
            platforms=['facebook']
        )
        
        record = PlatformPublishRecord.objects.create(
            transaction=post,
            platform='facebook',
            status=PlatformPublishRecord.Status.PENDING
        )
        
        assert record.transaction == post
        assert record.platform == 'facebook'
        assert record.status == 'PENDING'
        assert record.retry_count == 0

    def test_successful_publish_record(self):
        """Test successful publish record."""
        post = PostTransaction.objects.create(
            content="Test",
            platforms=['facebook']
        )
        
        record = PlatformPublishRecord.objects.create(
            transaction=post,
            platform='facebook',
            status=PlatformPublishRecord.Status.PUBLISHED,
            platform_post_id='123456_789',
            platform_url='https://facebook.com/123456_789',
            published_at=timezone.now()
        )
        
        assert record.status == 'PUBLISHED'
        assert record.platform_post_id is not None
        assert record.published_at is not None

    def test_failed_publish_record(self):
        """Test failed publish record with error."""
        post = PostTransaction.objects.create(
            content="Test",
            platforms=['facebook']
        )
        
        record = PlatformPublishRecord.objects.create(
            transaction=post,
            platform='facebook',
            status=PlatformPublishRecord.Status.FAILED,
            error_message="Token expired",
            error_code="190",
            retry_count=3
        )
        
        assert record.status == 'FAILED'
        assert record.error_message == "Token expired"
        assert record.error_code == "190"
        assert record.retry_count == 3

    def test_unique_together_constraint(self):
        """Test that transaction+platform must be unique."""
        post = PostTransaction.objects.create(
            content="Test",
            platforms=['facebook']
        )
        
        # First record should succeed
        PlatformPublishRecord.objects.create(
            transaction=post,
            platform='facebook',
            status=PlatformPublishRecord.Status.PENDING
        )
        
        # Second record with same transaction+platform should fail
        with pytest.raises(Exception):
            PlatformPublishRecord.objects.create(
                transaction=post,
                platform='facebook',
                status=PlatformPublishRecord.Status.PENDING
            )


@pytest.mark.django_db
class TestLineAudience:
    """Tests for LineAudience model."""

    def test_create_line_audience(self):
        """Test creating LINE audience member."""
        user = LineAudience.objects.create(
            line_user_id="U1234567890abcdef",
            display_name="Test User",
            profile_picture_url="https://example.com/pic.jpg"
        )
        
        assert user.line_user_id == "U1234567890abcdef"
        assert user.display_name == "Test User"
        assert user.is_active is True
        assert user.is_blocked is False
        assert user.message_count == 0

    def test_add_tag(self):
        """Test adding tags to user."""
        user = LineAudience.objects.create(
            line_user_id="U1234567890abcdef"
        )
        
        user.add_tag('vip')
        user.add_tag('newsletter')
        
        user.refresh_from_db()
        assert 'vip' in user.tags
        assert 'newsletter' in user.tags
        assert len(user.tags) == 2

    def test_remove_tag(self):
        """Test removing tags from user."""
        user = LineAudience.objects.create(
            line_user_id="U1234567890abcdef",
            tags=['vip', 'newsletter', 'premium']
        )
        
        user.remove_tag('newsletter')
        
        user.refresh_from_db()
        assert 'vip' in user.tags
        assert 'premium' in user.tags
        assert 'newsletter' not in user.tags
        assert len(user.tags) == 2

    def test_get_by_tags_any(self):
        """Test getting users by any matching tag."""
        user1 = LineAudience.objects.create(
            line_user_id="U111",
            tags=['vip', 'newsletter']
        )
        user2 = LineAudience.objects.create(
            line_user_id="U222",
            tags=['premium', 'newsletter']
        )
        user3 = LineAudience.objects.create(
            line_user_id="U333",
            tags=['basic']
        )
        
        # Get users with vip OR premium
        results = LineAudience.get_by_tags(['vip', 'premium'], all_tags=False)
        assert user1 in results
        assert user2 in results
        assert user3 not in results

    def test_get_by_tags_all(self):
        """Test getting users by all matching tags."""
        user1 = LineAudience.objects.create(
            line_user_id="U111",
            tags=['vip', 'newsletter', 'active']
        )
        user2 = LineAudience.objects.create(
            line_user_id="U222",
            tags=['vip', 'active']
        )
        user3 = LineAudience.objects.create(
            line_user_id="U333",
            tags=['newsletter', 'active']
        )
        
        # Get users with vip AND newsletter
        results = LineAudience.get_by_tags(['vip', 'newsletter'], all_tags=True)
        assert user1 in results
        assert user2 not in results
        assert user3 not in results

    def test_str_representation(self):
        """Test string representation."""
        user = LineAudience.objects.create(
            line_user_id="U1234567890abcdef",
            display_name="Test User"
        )
        
        assert "Test User" in str(user)
        assert "active" in str(user)
        
        # Test with inactive user
        user.is_active = False
        user.save()
        assert "inactive" in str(user)
