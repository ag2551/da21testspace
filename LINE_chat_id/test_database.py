"""
Test script for database functionality.
Tests user creation, updates, and queries.
"""

from datetime import datetime
from database import SessionLocal
from models import User


def test_new_user_creation():
    """Test creating a new user in the database."""
    print("\n" + "="*60)
    print("TEST 1: New User Creation")
    print("="*60)

    db = SessionLocal()
    try:
        # Create a test user
        test_user = User(
            line_user_id="U1234567890test",
            display_name="Test User",
            picture_url="https://example.com/picture.jpg",
            status_message="Hello from test!",
            language="en"
        )

        db.add(test_user)
        db.commit()
        print("✓ Test user created successfully")

        # Query the user back
        queried_user = db.query(User).filter(
            User.line_user_id == "U1234567890test"
        ).first()

        if queried_user:
            print(f"✓ User found in database:")
            print(f"  - ID: {queried_user.line_user_id}")
            print(f"  - Name: {queried_user.display_name}")
            print(f"  - Picture: {queried_user.picture_url}")
            print(f"  - Status: {queried_user.status_message}")
            print(f"  - Language: {queried_user.language}")
            print(f"  - Created: {queried_user.created_at}")
            print(f"  - Updated: {queried_user.updated_at}")
            return True
        else:
            print("❌ User not found in database")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def test_user_update():
    """Test updating an existing user."""
    print("\n" + "="*60)
    print("TEST 2: User Update")
    print("="*60)

    db = SessionLocal()
    try:
        # Find the test user
        user = db.query(User).filter(
            User.line_user_id == "U1234567890test"
        ).first()

        if not user:
            print("❌ Test user not found")
            return False

        # Store original timestamp
        original_updated_at = user.updated_at
        print(f"Original updated_at: {original_updated_at}")

        # Update user
        import time
        time.sleep(1)  # Wait 1 second to ensure timestamp changes

        user.display_name = "Updated Test User"
        user.updated_at = datetime.utcnow()
        db.commit()

        # Query again to verify
        updated_user = db.query(User).filter(
            User.line_user_id == "U1234567890test"
        ).first()

        print(f"✓ User updated successfully")
        print(f"  - New name: {updated_user.display_name}")
        print(f"  - New updated_at: {updated_user.updated_at}")

        if updated_user.updated_at > original_updated_at:
            print(f"✓ Timestamp updated correctly")
            return True
        else:
            print(f"❌ Timestamp not updated")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def test_user_queries():
    """Test various database queries."""
    print("\n" + "="*60)
    print("TEST 3: Database Queries")
    print("="*60)

    db = SessionLocal()
    try:
        # Count all users
        total_users = db.query(User).count()
        print(f"✓ Total users in database: {total_users}")

        # Get all users
        all_users = db.query(User).all()
        print(f"✓ Retrieved {len(all_users)} users")

        for user in all_users:
            print(f"  - {user.display_name or 'Unknown'} ({user.line_user_id})")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        db.close()


def test_cleanup():
    """Clean up test data."""
    print("\n" + "="*60)
    print("CLEANUP: Removing Test Data")
    print("="*60)

    db = SessionLocal()
    try:
        # Delete test user
        user = db.query(User).filter(
            User.line_user_id == "U1234567890test"
        ).first()

        if user:
            db.delete(user)
            db.commit()
            print("✓ Test user deleted successfully")
        else:
            print("⚠ Test user not found (already deleted?)")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# DATABASE FUNCTIONALITY TESTS")
    print("#"*60)

    results = []

    # Run tests
    results.append(("New User Creation", test_new_user_creation()))
    results.append(("User Update", test_user_update()))
    results.append(("Database Queries", test_user_queries()))
    results.append(("Cleanup", test_cleanup()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! Database is working correctly.")
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please review the output above.")
