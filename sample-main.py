"""
Sample usage of the Social Posts API.

This demonstrates CRUD operations across LinkedIn, Facebook, and Line Bot.
"""

from social_posts import (
    create_post, get_post, list_posts, update_post, delete_post,
    Platform, Body, BodyFormat, Image, ImageType, Reference, ReferenceType,
    NotFoundError, UnsupportedOperationError, PlatformError
)


def demo_create():
    """Demonstrate creating posts on different platforms."""

    # Simple text post to LinkedIn
    linkedin_post = create_post(
        platform=Platform.LINKEDIN,
        body=Body(content="Excited to share our latest project update!")
    )
    print(f"Created LinkedIn post: {linkedin_post.id}")

    # Rich HTML post to Facebook with image
    facebook_post = create_post(
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
    print(f"Created Facebook post: {facebook_post.id}")

    # Markdown post to Line Bot
    line_post = create_post(
        platform=Platform.LINE,
        body=Body(
            content="## Daily Update\n\n- Item 1\n- Item 2\n- Item 3",
            format=BodyFormat.MARKDOWN
        ),
        image=Image(type=ImageType.FILE, data="/path/to/local/image.png")
    )
    print(f"Created Line post: {line_post.id}")

    return linkedin_post, facebook_post, line_post


def demo_read(post_id: str):
    """Demonstrate reading a post."""

    try:
        post = get_post(post_id)
        print(f"Retrieved post: {post.id}")
        print(f"  Platform: {post.platform.value}")
        print(f"  Content: {post.body.content[:50]}...")
        print(f"  Created: {post.created_at}")
        return post
    except NotFoundError:
        print(f"Post {post_id} not found")
        return None


def demo_list():
    """Demonstrate listing posts with filtering."""

    # List all posts
    all_posts, total = list_posts()
    print(f"Total posts: {total}")

    # List only LinkedIn posts
    linkedin_posts, linkedin_total = list_posts(
        platform=Platform.LINKEDIN,
        limit=10,
        offset=0
    )
    print(f"LinkedIn posts: {linkedin_total}")

    # Paginate through Facebook posts
    page = 0
    page_size = 5
    while True:
        posts, total = list_posts(
            platform=Platform.FACEBOOK,
            limit=page_size,
            offset=page * page_size
        )
        if not posts:
            break
        print(f"Facebook page {page + 1}: {len(posts)} posts")
        page += 1


def demo_update(post_id: str):
    """Demonstrate updating a post."""

    try:
        # Update just the body
        updated = update_post(
            post_id=post_id,
            body=Body(content="Updated content with new information!")
        )
        print(f"Updated post: {updated.id}")
        print(f"  New content: {updated.body.content}")

        # Update image and references
        updated = update_post(
            post_id=post_id,
            image=Image(type=ImageType.URL, data="https://example.com/new-image.jpg"),
            references=[
                Reference(type=ReferenceType.LINK, value="New Link", url="https://new.example.com")
            ]
        )
        print(f"Updated post image and references")

        return updated

    except NotFoundError:
        print(f"Post {post_id} not found")
    except UnsupportedOperationError:
        print(f"Cannot update this post (Line Bot does not support updates)")

    return None


def demo_delete(post_id: str):
    """Demonstrate deleting a post."""

    try:
        success = delete_post(post_id)
        if success:
            print(f"Deleted post: {post_id}")
        return success
    except NotFoundError:
        print(f"Post {post_id} not found")
        return False


def demo_line_update_workaround(post_id: str):
    """
    Line Bot doesn't support updates.
    Workaround: delete and recreate.
    """

    # First, get the existing post
    original = get_post(post_id)

    if original.platform != Platform.LINE:
        # Not a Line post, use normal update
        return update_post(post_id, body=Body(content="New content"))

    # Delete the original
    delete_post(post_id)

    # Recreate with updated content
    new_post = create_post(
        platform=Platform.LINE,
        body=Body(content="New content", format=original.body.format),
        image=original.image,
        references=original.references
    )

    print(f"Recreated Line post: {original.id} -> {new_post.id}")
    return new_post


def main():
    """Run all demos."""

    print("=" * 50)
    print("Social Posts API Demo")
    print("=" * 50)

    # Create
    print("\n--- CREATE ---")
    linkedin_post, facebook_post, line_post = demo_create()

    # Read
    print("\n--- READ ---")
    demo_read(linkedin_post.id)

    # List
    print("\n--- LIST ---")
    demo_list()

    # Update
    print("\n--- UPDATE ---")
    demo_update(linkedin_post.id)
    demo_update(facebook_post.id)

    # Line update workaround
    print("\n--- LINE UPDATE WORKAROUND ---")
    demo_line_update_workaround(line_post.id)

    # Delete
    print("\n--- DELETE ---")
    demo_delete(linkedin_post.id)
    demo_delete(facebook_post.id)

    print("\n" + "=" * 50)
    print("Demo complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
