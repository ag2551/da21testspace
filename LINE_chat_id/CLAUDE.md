# Project Context: LINE Messaging Management API (FastAPI + Native SQLite)

## Project Overview
A dedicated API to manage LINE Messaging API push messages.
**Key Architecture**: This project uses **Native SQLite (aiosqlite)**. No ORM (SQLAlchemy/SQLModel) is used.

## Tech Stack
- **Framework**: FastAPI (Python 3.12)
- **Database**: SQLite (via `aiosqlite` driver)
- **Schema Validation**: Pydantic (V2)
- **HTTP Client**: httpx (Async)
- **Environment**: python-dotenv for secrets

## Architecture & Patterns
- **Database Access**:
  - **NO ORM ALLOWED**. Use raw SQL queries: `await db.execute("SELECT * FROM ...")`.
  - Use `aiosqlite.Row` as row_factory.
  - Connection management via FastAPI Dependency (`get_db_connection`).
- **Schema Management**:
  - Database tables are initialized via raw `CREATE TABLE IF NOT EXISTS` SQL strings in `app/database.py`.
  - **Simplified Schema**: Tables are optimized for LINE only (no generic social fields).
- **Service Layer**: Logic is contained in `LineService` (or Adapter) to handle API interactions.

## LINE Messaging API Logic
Logic is strictly defined due to API limitations:
- **Create (Publish)**:
  - API: `POST /v2/bot/message/push`
  - Auth: Channel Access Token + User ID (Target ID).
  - Store: Save returned `messageId` to `message_id` column.
- **Read**:
  - Do NOT call LINE API. Return DB timestamp (`created_at`).
- **Delete (Soft Delete)**:
  - **⚠️ IMPORTANT**: LINE Messaging API does NOT provide an unsend endpoint for bot messages.
  - Verified: All 68 methods in MessagingApi checked - no delete/unsend capability exists.
  - Implementation: Mark message as 'deleted' status in database only.
  - Note: Message remains permanently visible in LINE app.
  - Return clear error message explaining API limitation.
- **Update (Send New Message)**:
  - **⚠️ IMPORTANT**: LINE API does not support deleting bot messages.
  - **Logic**:
    1. Retrieve existing post data from DB.
    2. Call `Push` (Create) with new content.
    3. Update DB with new `message_id` and timestamp.
    4. Note: Original message remains visible in LINE (API limitation).

## Coding Conventions
- **Async/Await**: All DB and Network I/O must be async.
- **SQL Injection Prevention**: Always use parameterized queries (e.g., `await db.execute("SELECT * FROM table WHERE id = ?", (id,))`).
- **Error Handling**: Return standard Pydantic models or HTTPExceptions.