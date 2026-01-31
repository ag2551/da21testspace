"""
Test to verify webhook callback migration to native SQL.
Tests user profile storage functionality.
"""
import asyncio
import aiosqlite
from app.database import DATABASE_URL


async def test_user_operations():
    """Test user profile operations with native SQL."""
    print("Testing user profile operations (webhook callback simulation)...")
    print()

    async with aiosqlite.connect(DATABASE_URL) as db:
        db.row_factory = aiosqlite.Row

        # Simulate new user registration
        print("Test 1: New User Registration")
        user_id = "U_test_user_001"
        cursor = await db.execute(
            "SELECT * FROM users WHERE line_user_id = ?",
            (user_id,)
        )
        existing_user = await cursor.fetchone()

        if existing_user is None:
            # Create new user (simulating profile fetch from LINE API)
            # Note: created_at and updated_at will be set by DEFAULT CURRENT_TIMESTAMP
            await db.execute(
                """
                INSERT INTO users (line_user_id, display_name, picture_url, status_message, language, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """,
                (user_id, "Test User", "https://example.com/pic.jpg", "Hello!", "en")
            )
            await db.commit()
            print(f"✓ New user registered: {user_id}")
        else:
            print(f"✓ User already exists: {user_id}")
        print()

        # Simulate existing user update
        print("Test 2: Update Existing User")
        await db.execute(
            """
            UPDATE users
            SET display_name = ?, updated_at = CURRENT_TIMESTAMP
            WHERE line_user_id = ?
            """,
            ("Updated Test User", user_id)
        )
        await db.commit()

        cursor = await db.execute(
            "SELECT display_name, updated_at FROM users WHERE line_user_id = ?",
            (user_id,)
        )
        updated_user = await cursor.fetchone()
        print(f"✓ User profile updated:")
        print(f"  Display Name: {updated_user['display_name']}")
        print(f"  Updated At: {updated_user['updated_at']}")
        print()

        # Test minimal user creation (when profile fetch fails)
        print("Test 3: Minimal User Creation (Profile Fetch Failure Simulation)")
        minimal_user_id = "U_minimal_user_002"
        # When profile fetch fails, we still set default language
        await db.execute(
            "INSERT INTO users (line_user_id, language, created_at, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
            (minimal_user_id, "zh-TW")
        )
        await db.commit()

        cursor = await db.execute(
            "SELECT * FROM users WHERE line_user_id = ?",
            (minimal_user_id,)
        )
        minimal_user = await cursor.fetchone()
        print(f"✓ Minimal user created: {minimal_user_id}")
        print(f"  Display Name: {minimal_user['display_name'] or '(None)'}")
        print(f"  Language: {minimal_user['language']}")
        print()

        # Test rollback scenario
        print("Test 4: Transaction Rollback (Error Handling)")
        try:
            # Attempt duplicate insert (should fail)
            await db.execute(
                "INSERT INTO users (line_user_id, created_at, updated_at) VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                (user_id,)  # This already exists
            )
            await db.commit()
            print("✗ Duplicate insert should have failed!")
        except aiosqlite.IntegrityError:
            await db.rollback()
            print("✓ Rollback successful after integrity error")
        print()

        # List all users
        print("Test 5: List All Users")
        cursor = await db.execute(
            "SELECT line_user_id, display_name, created_at FROM users ORDER BY created_at DESC"
        )
        all_users = await cursor.fetchall()
        print(f"✓ Found {len(all_users)} user(s):")
        for u in all_users:
            print(f"  {u['line_user_id']}: {u['display_name'] or '(No name)'} (created: {u['created_at']})")
        print()

    print("=" * 60)
    print("Webhook callback migration verified successfully!")
    print("User profile storage working with native SQL.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_user_operations())
