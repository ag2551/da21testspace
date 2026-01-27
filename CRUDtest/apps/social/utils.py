"""
Social Media Hub - Utility Functions

This module provides utility functions for working with
Wagtail StreamFields and social media content.
"""

from typing import Dict, Any, List, Optional
from django.utils.html import strip_tags
from wagtail.rich_text import expand_db_html
from wagtail.fields import StreamField
import io


class StreamFieldSerializer:
    """
    Utility class for converting StreamField to various formats.
    
    This class provides methods to extract and transform Wagtail
    StreamField data for use with social media APIs.
    """

    @staticmethod
    def to_dict(streamfield: StreamField) -> List[Dict[str, Any]]:
        """
        Convert StreamField to list of dicts.

        Args:
            streamfield: Wagtail StreamField instance

        Returns:
            List of dictionaries with block data:
            [
                {"type": "heading", "value": "My Heading", "id": "..."},
                {"type": "paragraph", "value": "<p>Content</p>", "id": "..."},
                ...
            ]
        """
        result = []
        try:
            for block in streamfield:
                result.append({
                    "type": block.block_type,
                    "value": block.value,
                    "id": str(block.id)
                })
        except (AttributeError, TypeError):
            pass
        
        return result

    @staticmethod
    def to_text(streamfield: StreamField) -> str:
        """
        Convert StreamField to plain text (for social media).
        
        This method extracts text content from StreamField blocks
        and formats it for social media platforms.

        Args:
            streamfield: Wagtail StreamField instance

        Returns:
            Plain text string suitable for social media posts
        """
        parts = []
        
        try:
            for block in streamfield:
                if block.block_type == 'post':
                    block_value = block.value
                    
                    # Headline
                    if 'headline' in block_value and block_value['headline']:
                        parts.append(block_value['headline'])

                    # Body (strip HTML tags)
                    if 'body' in block_value and block_value['body']:
                        try:
                            html = expand_db_html(block_value['body'])
                            text = strip_tags(html)
                            if text.strip():
                                parts.append(text)
                        except Exception:
                            # If expansion fails, try to get raw text
                            raw = str(block_value['body'])
                            text = strip_tags(raw)
                            if text.strip():
                                parts.append(text)

                    # CTA (Call-to-action)
                    if (block_value.get('cta_text') and 
                        block_value.get('cta_url')):
                        cta = f"{block_value['cta_text']}: {block_value['cta_url']}"
                        parts.append(cta)
        
        except (AttributeError, TypeError, KeyError):
            pass

        return '\n\n'.join(parts)

    @staticmethod
    def extract_media(streamfield: StreamField) -> Optional[bytes]:
        """
        Extract first image from StreamField as bytes.
        
        This method finds the first image in the StreamField
        and returns it as bytes for upload to social platforms.

        Args:
            streamfield: Wagtail StreamField instance

        Returns:
            Image data as bytes, or None if no image found
        """
        try:
            for block in streamfield:
                if block.block_type == 'post':
                    image = block.value.get('image')
                    if image:
                        # Open the image file and read as bytes
                        with image.file.open('rb') as f:
                            return f.read()
        except (AttributeError, TypeError, KeyError, IOError):
            pass
        
        return None

    @staticmethod
    def extract_image_url(streamfield: StreamField) -> Optional[str]:
        """
        Extract first image URL from StreamField.

        Args:
            streamfield: Wagtail StreamField instance

        Returns:
            Image URL as string, or None if no image found
        """
        try:
            for block in streamfield:
                if block.block_type == 'post':
                    image = block.value.get('image')
                    if image:
                        return image.file.url
        except (AttributeError, TypeError, KeyError):
            pass
        
        return None

    @staticmethod
    def extract_headline(streamfield: StreamField) -> str:
        """
        Extract headline from StreamField.

        Args:
            streamfield: Wagtail StreamField instance

        Returns:
            Headline text, or empty string if not found
        """
        try:
            for block in streamfield:
                if block.block_type == 'post':
                    headline = block.value.get('headline')
                    if headline:
                        return headline
        except (AttributeError, TypeError, KeyError):
            pass
        
        return ""

    @staticmethod
    def extract_cta(streamfield: StreamField) -> Optional[Dict[str, str]]:
        """
        Extract call-to-action from StreamField.

        Args:
            streamfield: Wagtail StreamField instance

        Returns:
            Dictionary with 'text' and 'url' keys, or None if no CTA
        """
        try:
            for block in streamfield:
                if block.block_type == 'post':
                    cta_text = block.value.get('cta_text')
                    cta_url = block.value.get('cta_url')
                    
                    if cta_text and cta_url:
                        return {
                            'text': cta_text,
                            'url': cta_url
                        }
        except (AttributeError, TypeError, KeyError):
            pass
        
        return None


def format_content_for_platform(content: str, platform: str, max_length: Optional[int] = None) -> str:
    """
    Format content for specific platform constraints.
    
    Args:
        content: The content text
        platform: Platform name ('facebook', 'linkedin', 'line')
        max_length: Optional maximum length to truncate to
    
    Returns:
        Formatted content string
    """
    # Platform-specific max lengths (if not specified)
    if max_length is None:
        max_lengths = {
            'facebook': 63206,  # Facebook has a very high limit
            'linkedin': 3000,   # LinkedIn post limit
            'line': 5000,       # LINE message limit
        }
        max_length = max_lengths.get(platform, 5000)
    
    # Truncate if needed
    if len(content) > max_length:
        content = content[:max_length - 3] + '...'
    
    return content


def validate_platforms(platforms: List[str]) -> bool:
    """
    Validate that platform names are supported.
    
    Args:
        platforms: List of platform names
    
    Returns:
        True if all platforms are valid, False otherwise
    """
    valid_platforms = {'facebook', 'linkedin', 'line'}
    return all(p in valid_platforms for p in platforms)


def get_platform_display_name(platform: str) -> str:
    """
    Get display name for platform.
    
    Args:
        platform: Platform identifier
    
    Returns:
        Human-readable platform name
    """
    display_names = {
        'facebook': 'Facebook',
        'linkedin': 'LinkedIn',
        'line': 'LINE',
    }
    return display_names.get(platform, platform.title())
