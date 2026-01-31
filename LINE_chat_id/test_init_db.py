"""
Test script to verify database initialization.
"""
import asyncio
from app.database import init_db

async def test_init():
    """Test database initialization."""
    print("Testing database initialization...")
    await init_db()
    print("\nDatabase initialization complete!")

if __name__ == "__main__":
    asyncio.run(test_init())
