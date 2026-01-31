# Task: Integrate the LINE Messaging API and refactor it to native SQLite (remove SQLAlchemy)

I need to significantly refactor and expand the functionality of the current FastAPI project.

**Core Changes:**

1. **Remove SQLAlchemy/SQLModel:** I no longer want to use an ORM.

2. **Adopt Native SQLite:** Please use the `aiosqlite` suite to directly write Raw SQL (SELECT, INSERT, UPDATE, DELETE) to manipulate the database.

3. **Add LINE Support:** Implement LINE's CRUD logic (including a special Update mechanism).

Please follow these guidelines when making changes:

## 1. System Architecture and Dependencies

- **Remove:** `sqlalchemy`, `sqlmodel`, `alembic` (if any).

- **Retain/Add:** `aiosqlite` (for asynchronous database connections), `pydantic` (for API data validation), `httpx` (for calling the LINE API). ## 2. Database Layer Rewrite

Please rewrite this file to provide the following functionality:

- **`get_db_connection`**: A FastAPI Dependency used to establish and return `aiosqlite.Connection` (requires setting `row_factory = aiosqlite.Row` to access data by field name).

- **`init_db`**: An initialization function that uses the native SQL command `CREATE TABLE IF NOT EXISTS` to create the `social_credentials` and `social_posts` tables.

- **Credential table**: Add `target_id` (TEXT) to store LINE User IDs.

- **Post table**: Add `line_post_id` (TEXT), `line_published_at` (DATETIME/TEXT), and `line_status` (TEXT).

## 3. Pydantic Models

Since the ORM Model has been removed, ensure that the Pydantic Model definitions in the `schemas` folder are complete for API Request/Response validation.

## 4. Implementing the Adapter

Create a `LineAdapter` with the following logic:

- **publish_post (Push Message)**:

  - POST `https://api.line.me/v2/bot/message/push`.

  - Return `messageId` upon success.

- **delete_post (Soft Delete)**:

  - **⚠️ API LIMITATION**: LINE Messaging API does NOT support deleting bot messages.

  - Implementation: Return success response indicating database status updated.

  - Note: Message marked as 'deleted' in database only; remains visible in LINE app.

- **update_post (Send New Message)**:

  - **⚠️ API LIMITATION**: Cannot delete original message.

  - Receive the old `line_post_id` and new content.

  - Call `publish_post` with new content.

  - Return the new `message_id`.

  - Note: Sends new message; original message remains visible in LINE.

## 5. Modify Routers Completely rewrite the database operation logic in the Router, **must use native SQL**:

- **Create Post:**

- `INSERT INTO social_posts (...) VALUES (...) RETURNING id` (or use cursor.lastrowid).

- After obtaining the ID, call `adapter.publish_post`.

- `UPDATE social_posts SET ... WHERE id = ...` Update the publication result.

- **Read:**

- `SELECT * FROM social_posts ...`.

- **Delete:**

  - First, retrieve the post ID.

  - `UPDATE social_posts SET line_status = 'deleted', updated_at = CURRENT_TIMESTAMP WHERE id = ...` (soft delete).

  - **⚠️ Note**: Message remains visible in LINE (API limitation).

- **Update:**

  - `SELECT *` retrieves the old data.

  - Call `adapter.publish_post` with new content.

  - `UPDATE social_posts SET content = ?, line_message_id = ?, line_published_at = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ...`.

  - **⚠️ Note**: Sends new message; original message stays visible in LINE.

## 6. Config

- Remove SQLAlchemy related settings.

- Add `LINE_CHANNEL_ACCESS_TOKEN` and `LINE_USER_ID`.

Please provide complete code modifications, especially the native SQL implementation in `database.py` and the SQL operations in the Router.