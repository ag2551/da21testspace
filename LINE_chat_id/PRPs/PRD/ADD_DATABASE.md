## FEATURE
Add User Database Persistence (SQLAlchemy)

## GOAL
Integrate a SQLite database using SQLAlchemy to store LINE user profiles.
We need to record the User ID, Display Name, and other profile details whenever a user interacts with the bot.

## STANDARDS
- Use **SQLAlchemy** (ORM) for database interactions.
- Use **Pydantic** (optional but good) or direct ORM models.
- Database File: `line_bot.db` (SQLite).

## TASKS

### 1. Create `./database.py`
- Setup SQLAlchemy `create_engine` and `SessionLocal`.
- Define `Base = declarative_base()`.
- Define a dependency function `get_db()` for FastAPI.

### 2. Create `./models.py`
- Define a `User` class inheriting from `Base`.
- **Columns**:
  - `line_user_id` (String, Primary Key, index=True)
  - `display_name` (String, nullable=True)
  - `picture_url` (String, nullable=True)
  - `status_message` (String, nullable=True)
  - `language` (String, default='zh-TW')
  - `created_at` (DateTime, default=datetime.utcnow)
  - `updated_at` (DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

### 3. Modify `./main.py`
- **Import**: `models.py` and `database.py`.
- **Startup**: Call `models.Base.metadata.create_all(bind=engine)` to initialize tables.
- **Webhook Logic (`callback`)**:
  - Inside the `MessageEvent` loop:
    1. Get `user_id = event.source.user_id`.
    2. Query database: `db.query(User).filter(User.line_user_id == user_id).first()`.
    3. **IF User Not Found (New User)**:
       - Call LINE API: `profile = await line_bot_api.get_profile(user_id)`.
       - Create new `User` object with profile data.
       - `db.add` and `db.commit`.
    4. **IF User Exists**:
       - Update `user.updated_at`.
       - Update `display_name` to keep it fresh.
       - `db.commit`.
  - **Error Handling**: Wrap the `get_profile` call in try-except (in case user blocked the bot).

## COMMANDS TO RUN
- Please install `sqlalchemy` first if not present.