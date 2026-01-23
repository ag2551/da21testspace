# Social Posts API Specification

A unified Python API for publishing media content to multiple social platforms.

## Supported Platforms

| Platform      | Create | Read | Update | Delete |
|---------------|--------|------|--------|--------|
| LinkedIn      | ✓      | ✓    | ✓      | ✓      |
| Facebook Page | ✓      | ✓    | ✓      | ✓      |
| Line Bot      | ✓      | ✓    | ✗      | ✓      |

> **Note:** Line Bot does not support updates. To modify a message, delete and recreate.

---

## Data Models

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional
from datetime import datetime


class Platform(Enum):
    LINKEDIN = "linkedin"
    FACEBOOK = "facebook"
    LINE = "line"


class ImageType(Enum):
    FILE = "file"      # Local file path
    URL = "url"        # Remote URL


class BodyFormat(Enum):
    PLAIN = "plain"
    HTML = "html"
    MARKDOWN = "markdown"


class ReferenceType(Enum):
    TEXT = "text"
    LINK = "link"


@dataclass
class Image:
    type: ImageType
    data: str  # File path or URL


@dataclass
class Body:
    content: str
    format: BodyFormat = BodyFormat.PLAIN


@dataclass
class Reference:
    type: ReferenceType
    value: str
    url: Optional[str] = None  # Required if type is LINK


@dataclass
class Post:
    id: str
    platform: Platform
    image: Optional[Image]
    body: Body
    references: list[Reference]
    created_at: datetime
    updated_at: datetime
```

---

## Functions

### Create Post

```python
def create_post(
    platform: Platform,
    body: Body,
    image: Optional[Image] = None,
    references: Optional[list[Reference]] = None
) -> Post:
    """
    Create a new post on the specified platform.

    Args:
        platform: Target platform (linkedin, facebook, line)
        body: Post content with format specification
        image: Optional image (file path or URL)
        references: Optional list of references/links

    Returns:
        Post: The created post object with ID and timestamps

    Raises:
        ValidationError: Invalid input data
        PlatformError: Platform-specific error
    """
```

**Example:**
```python
post = create_post(
    platform=Platform.LINKEDIN,
    body=Body(content="Check out our latest update!", format=BodyFormat.PLAIN),
    image=Image(type=ImageType.URL, data="https://example.com/image.jpg"),
    references=[
        Reference(type=ReferenceType.LINK, value="Learn more", url="https://example.com")
    ]
)
```

---

### Read Post

```python
def get_post(post_id: str) -> Post:
    """
    Retrieve a post by ID.

    Args:
        post_id: Unique post identifier

    Returns:
        Post: The post object

    Raises:
        NotFoundError: Post does not exist
    """
```

---

### List Posts

```python
def list_posts(
    platform: Optional[Platform] = None,
    limit: int = 20,
    offset: int = 0
) -> tuple[list[Post], int]:
    """
    List posts with optional filtering.

    Args:
        platform: Filter by platform (None for all)
        limit: Maximum number of results
        offset: Pagination offset

    Returns:
        tuple: (list of posts, total count)
    """
```

---

### Update Post

```python
def update_post(
    post_id: str,
    body: Optional[Body] = None,
    image: Optional[Image] = None,
    references: Optional[list[Reference]] = None
) -> Post:
    """
    Update an existing post.

    Args:
        post_id: Post to update
        body: New content (None to keep existing)
        image: New image (None to keep existing)
        references: New references (None to keep existing)

    Returns:
        Post: The updated post object

    Raises:
        NotFoundError: Post does not exist
        UnsupportedOperationError: Platform does not support updates (Line Bot)
    """
```

---

### Delete Post

```python
def delete_post(post_id: str) -> bool:
    """
    Delete a post.

    Args:
        post_id: Post to delete

    Returns:
        bool: True if deleted successfully

    Raises:
        NotFoundError: Post does not exist
    """
```

---

## Exceptions

```python
class SocialPostError(Exception):
    """Base exception for all API errors."""
    pass


class ValidationError(SocialPostError):
    """Invalid input data."""
    pass


class NotFoundError(SocialPostError):
    """Resource not found."""
    pass


class UnsupportedOperationError(SocialPostError):
    """Operation not supported on this platform."""
    pass


class PlatformError(SocialPostError):
    """Platform-specific error (rate limit, auth, etc.)."""
    pass
```

---

## Image Handling

- **File:** Provide local file path in `Image.data`
- **URL:** Provide remote URL in `Image.data`
- Supported formats: JPEG, PNG, GIF
- Max file size: 5MB

---

## Example Usage

### Quick Start

```python
from social_posts import (
    create_post, get_post, list_posts, update_post, delete_post,
    Platform, Body, BodyFormat, Image, ImageType, Reference, ReferenceType
)

# Create a simple post
post = create_post(
    platform=Platform.LINKEDIN,
    body=Body(content="Hello from the API!")
)

# Read it back
retrieved = get_post(post.id)

# Update it
updated = update_post(post.id, body=Body(content="Updated content"))

# Delete it
delete_post(post.id)
```

### Create Posts by Platform

**LinkedIn - Simple text:**
```python
post = create_post(
    platform=Platform.LINKEDIN,
    body=Body(content="Excited to share our latest project update!")
)
```

**Facebook - Rich HTML with image and references:**
```python
post = create_post(
    platform=Platform.FACEBOOK,
    body=Body(
        content="<h2>New Product Launch</h2><p>Check out what we've been working on!</p>",
        format=BodyFormat.HTML
    ),
    image=Image(type=ImageType.URL, data="https://example.com/product.jpg"),
    references=[
        Reference(type=ReferenceType.LINK, value="Shop Now", url="https://shop.example.com"),
        Reference(type=ReferenceType.TEXT, value="Limited time offer")
    ]
)
```

**Line Bot - Markdown with local image:**
```python
post = create_post(
    platform=Platform.LINE,
    body=Body(
        content="## Daily Update\n\n- Item 1\n- Item 2",
        format=BodyFormat.MARKDOWN
    ),
    image=Image(type=ImageType.FILE, data="/path/to/local/image.png")
)
```

### List and Filter Posts

```python
# List all posts
all_posts, total = list_posts()

# Filter by platform
linkedin_posts, count = list_posts(platform=Platform.LINKEDIN)

# Paginate
page1, total = list_posts(limit=10, offset=0)
page2, total = list_posts(limit=10, offset=10)
```

### Handle Line Bot Updates (Workaround)

Line Bot does not support updates. Delete and recreate instead:

```python
def update_line_post(post_id: str, new_content: str):
    original = get_post(post_id)
    delete_post(post_id)
    return create_post(
        platform=Platform.LINE,
        body=Body(content=new_content, format=original.body.format),
        image=original.image,
        references=original.references
    )
```

### Error Handling

```python
from social_posts import NotFoundError, UnsupportedOperationError, PlatformError

try:
    post = get_post("invalid_id")
except NotFoundError:
    print("Post not found")

try:
    update_post(line_post_id, body=Body(content="New"))
except UnsupportedOperationError:
    print("Line Bot does not support updates")

try:
    create_post(platform=Platform.FACEBOOK, body=Body(content="Test"))
except PlatformError as e:
    print(f"Platform error: {e}")
```

---

## Sample Application

See `sample_main.py` for a complete demo application that exercises all CRUD operations:

```bash
python sample_main.py
```
