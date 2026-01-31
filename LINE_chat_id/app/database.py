"""
Database configuration and initialization for LINE Messaging API.
Uses native SQLite with aiosqlite for async operations.
No ORM - all operations use raw SQL queries.
"""

import aiosqlite
from typing import AsyncGenerator

DATABASE_URL = "line_bot.db"


async def get_db_connection() -> AsyncGenerator[aiosqlite.Connection, None]:
    """
    FastAPI dependency for database connections.
    Provides aiosqlite.Connection with row_factory set for dict-like access.

    Usage:
        @app.post("/endpoint")
        async def endpoint(db: aiosqlite.Connection = Depends(get_db_connection)):
            cursor = await db.execute("SELECT * FROM table WHERE id = ?", (id,))
            row = await cursor.fetchone()
            return dict(row)
    """
    db = await aiosqlite.connect(DATABASE_URL)
    db.row_factory = aiosqlite.Row  # Enable dict-like access to rows
    try:
        yield db
    finally:
        await db.close()


async def init_db():
    """
    Initialize database tables using raw SQL.
    Creates tables if they don't exist with proper schema.
    """
    async with aiosqlite.connect(DATABASE_URL) as db:
        # Create social_credentials table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS social_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                channel_access_token TEXT NOT NULL,
                channel_secret TEXT,
                target_id TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create social_posts table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS social_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL DEFAULT 'line',
                content TEXT NOT NULL,
                credential_id INTEGER,
                line_message_id TEXT,
                line_published_at DATETIME,
                line_status TEXT DEFAULT 'draft',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (credential_id) REFERENCES social_credentials(id)
            )
        """)

        # Create users table (migrated from ORM)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                line_user_id TEXT PRIMARY KEY,
                display_name TEXT,
                picture_url TEXT,
                status_message TEXT,
                language TEXT DEFAULT 'zh-TW',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for performance
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_created_at
            ON users(created_at)
        """)

        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_users_updated_at
            ON users(updated_at)
        """)

        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_posts_status
            ON social_posts(line_status)
        """)

        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_posts_created_at
            ON social_posts(created_at)
        """)

        await db.commit()
        print("✓ Database tables created successfully")
        print("  - social_credentials")
        print("  - social_posts")
        print("  - users")
        print("  - Indexes created for performance")
