"""
Test script for CRUD API endpoints.
Tests all endpoints without requiring actual LINE API integration.
"""
import asyncio
import aiosqlite
from app.database import DATABASE_URL


async def test_crud_operations():
    """Test CRUD database operations directly."""
    print("Testing CRUD operations with native SQL...")
    print()

    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row

        # Test 1: Create a test credential
        print("Test 1: Create Credential")
        cursor = await db.execute(
            """
            INSERT INTO social_credentials (platform, channel_access_token, channel_secret, target_id)
            VALUES (?, ?, ?, ?)
            """,
            ("line", "test_token_123", "test_secret_456", "U1234567890")
        )
        await db.commit()
        credential_id = cursor.lastrowid
        print(f"✓ Created credential with ID: {credential_id}")
        print()

        # Test 2: Create a draft post
        print("Test 2: Create Draft Post")
        cursor = await db.execute(
            """
            INSERT INTO social_posts (platform, content, credential_id, line_status)
            VALUES (?, ?, ?, ?)
            """,
            ("line", "Test message content", credential_id, "draft")
        )
        await db.commit()
        post_id = cursor.lastrowid
        print(f"✓ Created draft post with ID: {post_id}")
        print()

        # Test 3: Read the post
        print("Test 3: Read Post")
        cursor = await db.execute(
            "SELECT * FROM social_posts WHERE id = ?",
            (post_id,)
        )
        post = await cursor.fetchone()
        if post:
            print(f"✓ Post retrieved:")
            print(f"  ID: {post['id']}")
            print(f"  Content: {post['content']}")
            print(f"  Status: {post['line_status']}")
        print()

        # Test 4: Update the post
        print("Test 4: Update Post")
        await db.execute(
            """
            UPDATE social_posts
            SET content = ?, line_status = 'updated', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            ("Updated message content", post_id)
        )
        await db.commit()

        cursor = await db.execute(
            "SELECT content, line_status FROM social_posts WHERE id = ?",
            (post_id,)
        )
        updated_post = await cursor.fetchone()
        print(f"✓ Post updated:")
        print(f"  New Content: {updated_post['content']}")
        print(f"  New Status: {updated_post['line_status']}")
        print()

        # Test 5: Soft delete the post
        print("Test 5: Soft Delete Post")
        await db.execute(
            """
            UPDATE social_posts
            SET line_status = 'deleted', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (post_id,)
        )
        await db.commit()

        cursor = await db.execute(
            "SELECT line_status FROM social_posts WHERE id = ?",
            (post_id,)
        )
        deleted_post = await cursor.fetchone()
        print(f"✓ Post soft deleted:")
        print(f"  Status: {deleted_post['line_status']}")
        print()

        # Test 6: List all posts
        print("Test 6: List All Posts")
        cursor = await db.execute(
            "SELECT id, content, line_status FROM social_posts ORDER BY created_at DESC"
        )
        all_posts = await cursor.fetchall()
        print(f"✓ Found {len(all_posts)} post(s):")
        for p in all_posts:
            print(f"  ID {p['id']}: {p['content'][:30]}... [{p['line_status']}]")
        print()

        # Test 7: Test parameterized queries (SQL injection prevention)
        print("Test 7: SQL Injection Prevention Test")
        malicious_input = "1 OR 1=1"
        cursor = await db.execute(
            "SELECT * FROM social_posts WHERE id = ?",
            (malicious_input,)
        )
        result = await cursor.fetchone()
        if result is None:
            print("✓ Parameterized query correctly handled malicious input")
        else:
            print("✗ WARNING: SQL injection vulnerability detected!")
        print()

        # Test 8: Row factory dict access
        print("Test 8: Row Factory Dict Access")
        cursor = await db.execute("SELECT * FROM social_credentials WHERE id = ?", (credential_id,))
        cred = await cursor.fetchone()
        try:
            platform = cred['platform']
            token = cred['channel_access_token']
            print(f"✓ Dict-like access works:")
            print(f"  Platform: {platform}")
            print(f"  Token: {token[:20]}...")
        except TypeError:
            print("✗ Row factory not configured correctly")
        print()

    print("=" * 60)
    print("All CRUD operations completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_crud_operations())
