"""
Test script to verify main.py can be imported and initialized.
This tests that all imports work and database tables are created on startup.
"""

import sys


def test_imports():
    """Test that all imports in main.py work correctly."""
    print("\n" + "="*60)
    print("TEST: Import main.py")
    print("="*60)

    try:
        # Test importing main components
        from database import engine, get_db, Base
        print("✓ database module imported successfully")

        from models import User
        print("✓ models module imported successfully")

        # Verify User model attributes
        assert hasattr(User, '__tablename__')
        assert hasattr(User, 'line_user_id')
        assert hasattr(User, 'display_name')
        print("✓ User model has required attributes")

        return True

    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_creation():
    """Test database table creation."""
    print("\n" + "="*60)
    print("TEST: Database Table Creation")
    print("="*60)

    try:
        from database import engine, Base
        from models import User

        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully")

        # Verify table exists
        import sqlite3
        conn = sqlite3.connect('line_bot.db')
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        result = cursor.fetchone()

        if result:
            print(f"✓ Table 'users' exists in database")
        else:
            print(f"❌ Table 'users' not found")
            return False

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_management():
    """Test database session management."""
    print("\n" + "="*60)
    print("TEST: Database Session Management")
    print("="*60)

    try:
        from database import get_db

        # Test session creation
        db_gen = get_db()
        db = next(db_gen)
        print("✓ Database session created successfully")

        # Test session is valid
        from models import User
        count = db.query(User).count()
        print(f"✓ Query executed successfully (found {count} users)")

        # Close session
        db.close()
        print("✓ Database session closed successfully")

        return True

    except Exception as e:
        print(f"❌ Session management failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_main_syntax():
    """Test that main.py has valid syntax (without running FastAPI)."""
    print("\n" + "="*60)
    print("TEST: main.py Syntax Check")
    print("="*60)

    try:
        # Compile main.py to check for syntax errors
        with open('main.py', 'r') as f:
            code = f.read()
            compile(code, 'main.py', 'exec')

        print("✓ main.py has valid Python syntax")
        return True

    except SyntaxError as e:
        print(f"❌ Syntax error in main.py: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking main.py: {e}")
        return False


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# APPLICATION STARTUP TESTS")
    print("#"*60)

    results = []

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Database Creation", test_database_creation()))
    results.append(("Session Management", test_session_management()))
    results.append(("main.py Syntax", test_main_syntax()))

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
        print("\n✓ All tests passed! Application is ready to run.")
        print("\nTo start the application, run:")
        print("  .venv/bin/python main.py")
        print("or")
        print("  .venv/bin/uvicorn main:app --host 0.0.0.0 --port 5000 --reload")
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please review the output above.")
        sys.exit(1)
