"""
Tests for Wagtail Content models.
"""

import pytest
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase
from apps.content.models import SocialPostPage, SocialPostBlock


@pytest.mark.django_db
class TestSocialPostPage(WagtailPageTestCase):
    """Tests for SocialPostPage model."""

    def setUp(self):
        """Set up test data."""
        # Get the root page
        self.root_page = Page.objects.get(id=1)

    def test_can_create_social_post_page(self):
        """Test that we can create a SocialPostPage."""
        page = SocialPostPage(
            title="Test Social Post",
            slug="test-social-post",
            publish_to_facebook=True,
            publish_to_linkedin=True,
            publish_to_line=False,
        )
        
        # Add to root page
        self.root_page.add_child(instance=page)
        page.save()
        
        assert page.id is not None
        assert page.title == "Test Social Post"
        assert page.publish_to_facebook is True
        assert page.publish_to_linkedin is True
        assert page.publish_to_line is False

    def test_get_selected_platforms(self):
        """Test get_selected_platforms method."""
        page = SocialPostPage(
            title="Test Post",
            slug="test-post",
            publish_to_facebook=True,
            publish_to_linkedin=False,
            publish_to_line=True,
        )
        
        self.root_page.add_child(instance=page)
        
        platforms = page.get_selected_platforms()
        assert 'facebook' in platforms
        assert 'line' in platforms
        assert 'linkedin' not in platforms
        assert len(platforms) == 2

    def test_page_parent_and_subpage_types(self):
        """Test page type rules."""
        # Create a social post page
        page = SocialPostPage(
            title="Test Post",
            slug="test-post",
        )
        self.root_page.add_child(instance=page)
        
        # Social post page should not allow subpages
        assert page.allowed_subpage_models() == []

    def test_str_representation(self):
        """Test string representation."""
        page = SocialPostPage(
            title="My Social Post",
            slug="my-social-post",
        )
        
        assert str(page) == "My Social Post"

    def test_verbose_names(self):
        """Test model verbose names."""
        assert SocialPostPage._meta.verbose_name == "Social Media Post"
        assert SocialPostPage._meta.verbose_name_plural == "Social Media Posts"


@pytest.mark.django_db
class TestSocialPostBlock:
    """Tests for SocialPostBlock."""

    def test_social_post_block_structure(self):
        """Test that SocialPostBlock has correct fields."""
        block = SocialPostBlock()
        
        # Check that all expected fields exist
        assert 'headline' in block.child_blocks
        assert 'body' in block.child_blocks
        assert 'image' in block.child_blocks
        assert 'cta_text' in block.child_blocks
        assert 'cta_url' in block.child_blocks

    def test_block_meta_properties(self):
        """Test block meta properties."""
        assert SocialPostBlock._meta_class.icon == 'doc-full'
        assert SocialPostBlock._meta_class.label == 'Social Post'
