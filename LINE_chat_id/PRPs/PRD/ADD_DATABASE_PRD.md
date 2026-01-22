# Product Requirement Document (PRD)
## User Database Persistence with SQLAlchemy

**Version**: 1.0
**Date**: 2026-01-21
**Author**: System Generated from ADD_DATABASE.md
**Status**: Draft - Awaiting Review

---

## 1. Executive Summary

### 1.1 Feature Overview
Implement persistent user profile storage using SQLAlchemy ORM with SQLite database. The system will automatically capture and store LINE user profile information (User ID, Display Name, Profile Picture URL, Status Message, Language) whenever users interact with the LINE chatbot. This creates a foundation for user analytics, personalization, and historical tracking.

### 1.2 Business Value
- **User Analytics**: Track total users, new vs. returning users, and engagement patterns
- **Personalization**: Enable personalized responses based on user history
- **Data Persistence**: Maintain user information even if bot restarts
- **Scalability Foundation**: Establish database architecture for future features (message history, preferences, etc.)
- **Regulatory Compliance**: Centralized user data management for GDPR/privacy requirements

### 1.3 Success Metrics
- All new users are successfully persisted to database on first interaction
- User profile updates occur within 100ms
- Database queries do not add more than 50ms latency to message responses
- Zero data loss during concurrent user interactions

---

## 2. User Stories

### 2.1 Primary User Story - Automatic Profile Capture
**As a** LINE user
**I want** my profile information to be automatically saved when I message the bot
**So that** the bot can recognize me and provide personalized experiences

**Acceptance Criteria**:
- When a new user sends their first message, their profile is fetched from LINE API and stored
- User ID, display name, profile picture URL, and status message are captured
- The process happens transparently without user awareness
- Subsequent messages from the same user do not re-fetch the profile unnecessarily

### 2.2 Developer Story - Database Management
**As a** developer
**I want** a clean SQLAlchemy ORM layer with proper session management
**So that** I can easily query and manage user data throughout the application

**Acceptance Criteria**:
- Database schema is automatically created on application startup
- FastAPI dependency injection provides database sessions to endpoints
- Sessions are properly closed after each request
- No database connection leaks occur

### 2.3 Operations Story - Profile Freshness
**As an** operations engineer
**I want** user profiles to be periodically refreshed
**So that** display name and status message changes are reflected in our database

**Acceptance Criteria**:
- User `updated_at` timestamp is updated on each interaction
- Display name is refreshed from LINE API on each user message
- Profile updates handle cases where users have blocked the bot gracefully

---

## 3. Technical Requirements

### 3.1 Technology Stack
| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| ORM | SQLAlchemy | ≥2.0 | Database abstraction and ORM |
| Database | SQLite | 3.x | Local file-based database |
| Framework | FastAPI | Latest | Dependency injection for sessions |
| Python | Python 3 | ≥3.10 | Runtime environment |

### 3.2 New Dependencies
Add to `requirements.txt`:
```
sqlalchemy>=2.0.0
```

### 3.3 Database Schema

#### 3.3.1 Users Table
**Table Name**: `users`

| Column Name | Type | Constraints | Description |
|-------------|------|-------------|-------------|
| `line_user_id` | String(255) | PRIMARY KEY, INDEX | LINE's unique user identifier |
| `display_name` | String(255) | NULLABLE | User's display name from LINE profile |
| `picture_url` | Text | NULLABLE | URL to user's profile picture |
| `status_message` | Text | NULLABLE | User's status message |
| `language` | String(10) | DEFAULT 'zh-TW' | User's preferred language |
| `created_at` | DateTime | NOT NULL, DEFAULT NOW | First time user interacted with bot |
| `updated_at` | DateTime | NOT NULL, DEFAULT NOW, ON UPDATE NOW | Last time user interacted with bot |

**Indexes**:
- PRIMARY KEY on `line_user_id`
- INDEX on `created_at` for analytics queries
- INDEX on `updated_at` for finding active users

### 3.4 Architecture Components

#### 3.4.1 Database Configuration (`database.py`)
**Purpose**: Centralized database connection and session management

**Key Components**:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./line_bot.db"

# Engine creation (SQLAlchemy 2.0 style)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Required for SQLite
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
class Base(DeclarativeBase):
    pass

# FastAPI dependency for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Design Decisions**:
- Use SQLite for simplicity (file: `line_bot.db` in project root)
- `check_same_thread=False` allows SQLite usage in async FastAPI context
- Session cleanup in `finally` block ensures no connection leaks
- Dependency injection pattern aligns with FastAPI best practices

#### 3.4.2 Database Models (`models.py`)
**Purpose**: Define ORM models for database tables

**User Model** (SQLAlchemy 2.0 style with type annotations):
```python
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column
from database import Base

class User(Base):
    __tablename__ = "users"

    line_user_id: Mapped[str] = mapped_column(String(255), primary_key=True, index=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255))
    picture_url: Mapped[Optional[str]] = mapped_column(Text)
    status_message: Mapped[Optional[str]] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String(10), default='zh-TW')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    __table_args__ = (
        Index('idx_created_at', 'created_at'),
        Index('idx_updated_at', 'updated_at'),
    )

    def __repr__(self) -> str:
        return f"User(line_user_id={self.line_user_id!r}, display_name={self.display_name!r})"
```

**Design Decisions**:
- Use SQLAlchemy 2.0 `Mapped` type annotations for better IDE support
- `line_user_id` as primary key (natural key from LINE platform)
- Separate `created_at` and `updated_at` for analytics
- `language` defaults to 'zh-TW' (Traditional Chinese) - can be customized

#### 3.4.3 Main Application Updates (`main.py`)

**Startup Modifications**:
```python
from database import engine, get_db
from models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    global async_api_client, line_bot_api, agent_runner

    # Create database tables on startup
    Base.metadata.create_all(bind=engine)

    # ... existing initialization code ...

    yield

    # ... existing cleanup code ...
```

**Webhook Logic Updates** (`/callback` endpoint):

**Current Flow**:
1. Receive webhook event
2. Parse message text
3. Generate AI response
4. Reply to user

**New Flow** (with database integration):
1. Receive webhook event
2. **Extract user_id from event**
3. **Check if user exists in database**
4. **If new user: Fetch profile from LINE API and create database record**
5. **If existing user: Update last interaction timestamp and display name**
6. Parse message text
7. Generate AI response
8. Reply to user

**Implementation**:
```python
from sqlalchemy.orm import Session
from fastapi import Depends
from models import User

@app.post("/callback")
async def callback(request: Request, db: Session = Depends(get_db)):
    # ... existing signature validation code ...

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            # NEW: Extract user ID
            user_id = event.source.user_id

            # NEW: Database operations
            try:
                # Check if user exists
                user = db.query(User).filter(User.line_user_id == user_id).first()

                if user is None:
                    # New user - fetch profile from LINE API
                    try:
                        profile = await line_bot_api.get_profile(user_id)

                        # Create new user record
                        new_user = User(
                            line_user_id=user_id,
                            display_name=profile.display_name,
                            picture_url=profile.picture_url,
                            status_message=profile.status_message,
                            language=getattr(profile, 'language', 'zh-TW')
                        )
                        db.add(new_user)
                        db.commit()
                        print(f"New user registered: {user_id} ({profile.display_name})")

                    except Exception as profile_error:
                        # Handle cases where profile fetch fails (user blocked bot, etc.)
                        print(f"Could not fetch profile for {user_id}: {profile_error}")
                        # Create minimal user record
                        new_user = User(line_user_id=user_id)
                        db.add(new_user)
                        db.commit()
                else:
                    # Existing user - update timestamp and display name
                    try:
                        profile = await line_bot_api.get_profile(user_id)
                        user.display_name = profile.display_name
                        user.updated_at = datetime.utcnow()
                        db.commit()
                    except Exception as profile_error:
                        # If profile fetch fails, just update timestamp
                        print(f"Could not refresh profile for {user_id}: {profile_error}")
                        user.updated_at = datetime.utcnow()
                        db.commit()

            except Exception as db_error:
                # Database errors should not break the chatbot
                print(f"Database error for user {user_id}: {db_error}")
                db.rollback()

            # ... existing message processing code ...
```

---

## 4. File Structure

### 4.1 New Files
```
/home/arexsguo/LINE_chat_id/
├── database.py          # NEW: Database configuration and session management
├── models.py            # NEW: SQLAlchemy ORM models
└── line_bot.db          # NEW: SQLite database file (auto-created)
```

### 4.2 Modified Files
```
/home/arexsguo/LINE_chat_id/
├── main.py              # MODIFIED: Add database integration to webhook
└── requirements.txt     # MODIFIED: Add sqlalchemy dependency
```

---

## 5. Implementation Plan

### 5.1 Phase 1: Database Setup
**Files**: `database.py`, `models.py`

**Tasks**:
1. Create `database.py` with engine, session factory, and Base class
2. Create `models.py` with User model using SQLAlchemy 2.0 syntax
3. Add imports in both files

**Validation**:
- Run `python -c "from database import engine; from models import Base; Base.metadata.create_all(engine)"` to verify table creation
- Check that `line_bot.db` file is created
- Verify no import errors

### 5.2 Phase 2: Dependency Installation
**Files**: `requirements.txt`

**Tasks**:
1. Add `sqlalchemy>=2.0.0` to requirements.txt
2. Install dependency: `pip install sqlalchemy`

**Validation**:
- Run `pip list | grep -i sqlalchemy` to confirm version ≥2.0
- Test import: `python -c "import sqlalchemy; print(sqlalchemy.__version__)"`

### 5.3 Phase 3: Main Application Integration
**Files**: `main.py`

**Tasks**:
1. Add imports for database, models, Session, datetime
2. Modify `lifespan` function to create tables on startup
3. Add `db: Session = Depends(get_db)` to callback function signature
4. Implement user lookup and profile fetching logic
5. Add error handling for profile fetch failures

**Validation**:
- Start application and verify tables are created
- Send test message from new LINE user
- Check database for new user record
- Send another message and verify timestamp updates

### 5.4 Phase 4: Testing and Edge Cases
**Tasks**:
1. Test with user who has blocked the bot (profile fetch should fail gracefully)
2. Test concurrent users (multiple messages at once)
3. Verify database session cleanup (no connection leaks)
4. Test with users who have no status message
5. Test with users who have very long display names or status messages

---

## 6. API Changes

### 6.1 LINE Messaging API Calls

**New API Call**: `line_bot_api.get_profile(user_id)`

**Endpoint**: `GET https://api.line.me/v2/bot/profile/{userId}`

**Headers**:
```
Authorization: Bearer {LINE_CHANNEL_ACCESS_TOKEN}
```

**Response**:
```json
{
  "userId": "U4af4980629...",
  "displayName": "LINE Botto",
  "pictureUrl": "https://profile.line-scdn.net/ch/v2/p/uf9da5ee2b...",
  "statusMessage": "Hello world!",
  "language": "en"
}
```

**Error Cases**:
- 400: Bad Request (invalid user_id)
- 404: User not found or has blocked the bot
- 401: Invalid access token

---

## 7. Testing & Verification

### 7.1 Unit Tests (Manual)

**Test 1: New User Registration**
```python
# Steps:
1. Clear database: rm line_bot.db
2. Start application
3. Send message from LINE user (User A) who has never messaged before
4. Check database:
   SELECT * FROM users WHERE line_user_id = 'U...';

# Expected:
- New record exists with correct display_name, picture_url, status_message
- created_at and updated_at are set to current timestamp
```

**Test 2: Existing User Update**
```python
# Steps:
1. Send another message from User A
2. Note the original updated_at timestamp
3. Send message again
4. Check database:
   SELECT updated_at FROM users WHERE line_user_id = 'U...';

# Expected:
- updated_at timestamp is newer than previous
- Only one record exists for User A (no duplicates)
```

**Test 3: Profile Fetch Failure**
```python
# Steps:
1. Temporarily set invalid LINE_CHANNEL_ACCESS_TOKEN in .env
2. Send message from new user (User B)
3. Check database and application logs

# Expected:
- Error is logged but application continues
- Minimal user record created (user_id only)
- Bot still responds to message
```

**Test 4: Concurrent Users**
```python
# Steps:
1. Send messages from 3 different LINE users simultaneously
2. Check database:
   SELECT COUNT(*) FROM users;

# Expected:
- All 3 users are registered
- No database lock errors in logs
```

### 7.2 Integration Tests

**Test 5: End-to-End Flow**
```
1. Fresh database (rm line_bot.db)
2. Start application with uvicorn
3. Send LINE message: "Hello"
4. Verify:
   - User profile fetched from LINE API
   - Database record created
   - AI response received
   - Total response time < 3 seconds
```

### 7.3 Performance Verification

**Metrics to Monitor**:
- Database query time: Should be < 50ms per operation
- Profile fetch time: LINE API typically responds in 200-500ms
- Total message latency increase: Should be < 1 second additional

**Monitoring Query**:
```python
import time

start = time.time()
user = db.query(User).filter(User.line_user_id == user_id).first()
query_time = time.time() - start
print(f"Database query took {query_time*1000:.2f}ms")
```

---

## 8. Error Handling

### 8.1 Database Errors

**Scenario**: Database connection fails or SQLite file is corrupted

**Handling**:
```python
try:
    # database operations
except Exception as db_error:
    print(f"Database error: {db_error}")
    db.rollback()
    # Continue processing message - bot functionality should not break
```

**User Impact**: None - bot continues to respond to messages even if database fails

### 8.2 LINE API Errors

**Scenario 1**: User has blocked the bot
- LINE API returns 404 or permission error
- **Handling**: Create minimal user record (user_id only) and log the error

**Scenario 2**: Invalid access token
- LINE API returns 401
- **Handling**: Log critical error - this indicates configuration issue

**Scenario 3**: Rate limiting
- LINE API returns 429
- **Handling**: Skip profile update, use existing data if available

### 8.3 Data Validation

**Long Text Fields**:
- SQLite TEXT type handles arbitrary length
- No truncation needed

**Missing Profile Fields**:
- All profile fields except `line_user_id` are NULLABLE
- Handle `None` values gracefully

---

## 9. Security & Privacy Considerations

### 9.1 Data Privacy
- **User Consent**: Profile data is automatically collected - ensure LINE ToS compliance
- **Data Retention**: No automatic deletion - consider implementing GDPR-compliant data retention policies
- **Access Control**: Database file should have restricted file permissions (600)

### 9.2 Sensitive Data
- Do not log `line_user_id` in production unless necessary for debugging
- Profile pictures are URLs, not stored locally
- Status messages may contain personal information - handle appropriately

### 9.3 Database Security
```bash
# Set proper file permissions on database
chmod 600 line_bot.db
```

---

## 10. Future Enhancements

### 10.1 Immediate Extensions
1. **Message History Table**: Store all messages exchanged with users
2. **User Preferences**: Store language preference, notification settings
3. **Analytics Dashboard**: Query database for user growth metrics

### 10.2 Advanced Features
1. **PostgreSQL Migration**: Switch from SQLite to PostgreSQL for production
2. **User Segmentation**: Add tags/groups for targeted messaging
3. **Conversation Context**: Store conversation history for better AI responses
4. **Profile Sync Scheduler**: Background job to refresh stale profiles

### 10.3 Database Migration Path
```python
# Example Alembic migration for adding new fields
def upgrade():
    op.add_column('users', sa.Column('last_message_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('message_count', sa.Integer(), default=0))
```

---

## 11. Rollback Plan

### 11.1 If Database Integration Fails

**Steps**:
1. Comment out database operations in `main.py`
2. Remove `db: Session = Depends(get_db)` from callback signature
3. Bot reverts to stateless mode (no user persistence)

**Code Change**:
```python
# Quick rollback - comment out database section
# try:
#     user = db.query(User).filter(...)
#     ...
# except Exception as db_error:
#     ...
```

### 11.2 Data Backup
```bash
# Before deployment
cp line_bot.db line_bot.db.backup

# If rollback needed
mv line_bot.db.backup line_bot.db
```

---

## 12. Success Criteria

### 12.1 Functional Requirements ✓
- [ ] New users are automatically registered on first message
- [ ] User profiles are fetched from LINE API successfully
- [ ] Database tables are created automatically on startup
- [ ] Existing users have updated timestamps on each message
- [ ] Profile fetch failures do not break the bot

### 12.2 Non-Functional Requirements ✓
- [ ] Database operations add < 100ms latency
- [ ] No database connection leaks (verified with long-running test)
- [ ] Application starts successfully with empty database
- [ ] Concurrent user messages are handled correctly
- [ ] Error logs are clear and actionable

### 12.3 Documentation ✓
- [ ] Code comments explain database integration points
- [ ] README updated with database setup instructions
- [ ] Schema documented in this PRD
- [ ] Error handling documented

---

## 13. Appendix

### 13.1 SQLAlchemy 2.0 vs 1.4 Syntax

**This PRD uses SQLAlchemy 2.0** for modern best practices:

**Old (1.4)**:
```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    line_user_id = Column(String, primary_key=True)
```

**New (2.0)**:
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    line_user_id: Mapped[str] = mapped_column(String(255), primary_key=True)
```

**Benefits of 2.0 syntax**:
- Better type hints and IDE autocomplete
- Clearer code with type annotations
- Future-proof (recommended by SQLAlchemy team)

### 13.2 Database Schema Diagram

```
┌─────────────────────────────────────────┐
│             users                       │
├─────────────────────────────────────────┤
│ line_user_id     VARCHAR(255)    PK     │
│ display_name     VARCHAR(255)    NULL   │
│ picture_url      TEXT             NULL   │
│ status_message   TEXT             NULL   │
│ language         VARCHAR(10)      'zh-TW'│
│ created_at       DATETIME         NOW()  │
│ updated_at       DATETIME         NOW()  │
└─────────────────────────────────────────┘
         │
         │ Indexes:
         ├─ PRIMARY KEY (line_user_id)
         ├─ INDEX idx_created_at (created_at)
         └─ INDEX idx_updated_at (updated_at)
```

### 13.3 Example Database Queries

**Get all users**:
```python
users = db.query(User).all()
```

**Get user by LINE ID**:
```python
user = db.query(User).filter(User.line_user_id == "U1234567890").first()
```

**Count total users**:
```python
total_users = db.query(User).count()
```

**Get users registered today**:
```python
from datetime import datetime, timedelta

today = datetime.utcnow().date()
new_users = db.query(User).filter(
    User.created_at >= today
).all()
```

**Get most active users** (when message_count is added):
```python
top_users = db.query(User).order_by(User.message_count.desc()).limit(10).all()
```

---

## 14. Approval & Sign-Off

**Prepared by**: System (generate-prp skill)
**Review Required by**: Product Owner, Tech Lead
**Expected Implementation Time**: 2-4 hours
**Risk Level**: Low (isolated database layer, no breaking changes)

**Next Steps**:
1. Review this PRD
2. Approve implementation approach
3. Execute implementation plan (Section 5)
4. Run verification tests (Section 7)
5. Deploy to development environment
