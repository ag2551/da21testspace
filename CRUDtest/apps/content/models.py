"""
Social Media Hub - Wagtail Content Models

This module defines Wagtail Page models for content management.
"""

from django.db import models
from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.blocks import CharBlock, RichTextBlock, StructBlock, URLBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.admin.panels import FieldPanel, MultiFieldPanel


class SocialPostBlock(StructBlock):
    """Custom block for social media posts."""
    
    headline = CharBlock(
        max_length=280,
        help_text="Post headline (max 280 chars for Twitter compatibility)"
    )
    
    body = RichTextBlock(
        help_text="Main post content (will be converted to plain text for social platforms)"
    )
    
    image = ImageChooserBlock(
        required=False,
        help_text="Optional post image (will be uploaded to each platform)"
    )
    
    cta_text = CharBlock(
        max_length=50,
        required=False,
        help_text="Call-to-action text (e.g., 'Learn More', 'Shop Now')"
    )
    
    cta_url = URLBlock(
        required=False,
        help_text="Call-to-action URL"
    )

    class Meta:
        icon = 'doc-full'
        label = 'Social Post'
        template = 'blocks/social_post_block.html'


class SocialPostPage(Page):
    """
    Wagtail page model for social media posts.
    
    This model is used to author content in the Wagtail CMS,
    which is then published to selected social media platforms.
    """

    # StreamField for flexible content composition
    content = StreamField(
        [
            ('post', SocialPostBlock()),
        ],
        use_json_field=True,
        help_text="Compose your social media post content"
    )

    # Platform selection
    publish_to_facebook = models.BooleanField(
        default=True,
        help_text="Publish this post to Facebook"
    )
    
    publish_to_linkedin = models.BooleanField(
        default=True,
        help_text="Publish this post to LinkedIn"
    )
    
    publish_to_line = models.BooleanField(
        default=False,
        help_text="Send this post to LINE followers"
    )

    # Scheduling
    scheduled_publish_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Schedule this post for future publishing (leave blank for immediate)"
    )

    # Wagtail admin panel configuration
    content_panels = Page.content_panels + [
        FieldPanel('content'),
        MultiFieldPanel(
            [
                FieldPanel('publish_to_facebook'),
                FieldPanel('publish_to_linkedin'),
                FieldPanel('publish_to_line'),
            ],
            heading="Publishing Platforms",
            help_text="Select which platforms to publish this post to"
        ),
        FieldPanel('scheduled_publish_time'),
    ]

    # Subpage/parent page rules
    # Can be created under any page (including root)
    parent_page_types = []  # Empty list means can be created under any page type
    subpage_types = []  # Cannot have children

    class Meta:
        verbose_name = "Social Media Post"
        verbose_name_plural = "Social Media Posts"

    def save(self, *args, **kwargs):
        """
        Override save to trigger publishing workflow.
        
        When a page is published (set to live), this triggers the
        Celery task to publish to selected platforms.
        """
        # Determine if this is a publish action (not just a save as draft)
        is_publishing = self.live and not self._state.adding
        
        # Save the page first
        super().save(*args, **kwargs)

        # If publishing, trigger the background task
        # TODO: Implement publish_to_platforms task in Phase 3
        if is_publishing:
            try:
                from apps.social.tasks import publish_to_platforms
                
                # Build list of selected platforms
                platforms = []
                if self.publish_to_facebook:
                    platforms.append('facebook')
                if self.publish_to_linkedin:
                    platforms.append('linkedin')
                if self.publish_to_line:
                    platforms.append('line')

                # Only trigger if at least one platform is selected
                if platforms:
                    if self.scheduled_publish_time:
                        # Schedule for future
                        publish_to_platforms.apply_async(
                            args=[self.id, platforms],
                            eta=self.scheduled_publish_time
                        )
                    else:
                        # Publish immediately
                        publish_to_platforms.delay(self.id, platforms)
            except ImportError:
                # Task not implemented yet (Phase 3)
                pass

    def get_selected_platforms(self) -> list[str]:
        """Return list of selected platforms."""
        platforms = []
        if self.publish_to_facebook:
            platforms.append('facebook')
        if self.publish_to_linkedin:
            platforms.append('linkedin')
        if self.publish_to_line:
            platforms.append('line')
        return platforms

    def __str__(self):
        return self.title
