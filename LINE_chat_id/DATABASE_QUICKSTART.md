# Database Feature - Quick Start Guide

## Overview

Your LINE bot now automatically saves user profile information to a SQLite database whenever users interact with it.

## What Gets Stored

When a user messages your bot, the following information is automatically saved:

- **LINE User ID** - Unique identifier from LINE
- **Display Name** - User's name on LINE
- **Profile Picture URL** - Link to their profile picture
- **Status Message** - Their LINE status message
- **Language** - Preferred language (default: zh-TW)
- **Created At** - When they first messaged the bot
- **Updated At** - Last time they messaged the bot

## Database Location

**File**: `line_bot.db` (created automatically in project root)
**Type**: SQLite database
**Size**: Starts at ~24KB, grows with users

## How It Works

### First-Time Users
```
User sends message → Bot detects new user → Fetches profile from LINE API
                   → Saves to database → Responds to message
```

Console output:
```
New user detected: U1234567890
✓ New user registered: U1234567890 (John Doe)
```

### Returning Users
```
User sends message → Bot finds existing user → Updates timestamp
                   → Refreshes display name → Responds to message
```

Console output:
```
✓ User profile updated: U1234567890 (John Doe)
```

## Checking Your Database

### View All Users (Command Line)
```bash
sqlite3 line_bot.db "SELECT line_user_id, display_name, created_at FROM users;"
```

### Count Total Users
```bash
sqlite3 line_bot.db "SELECT COUNT(*) as total_users FROM users;"
```

### View Recent Users
```bash
sqlite3 line_bot.db "SELECT display_name, created_at FROM users ORDER BY created_at DESC LIMIT 10;"
```

### Query with Python
```python
from database import SessionLocal
from models import User

db = SessionLocal()

# Get all users
users = db.query(User).all()
for user in users:
    print(f"{user.display_name} - Last active: {user.updated_at}")

# Count users
print(f"Total users: {db.query(User).count()}")

db.close()
```

## Testing

### Run All Tests
```bash
# Test database functionality
.venv/bin/python test_database.py

# Test application startup
.venv/bin/python test_startup.py
```

Both should show:
```
✓ All tests passed!
```

## Common Use Cases

### 1. View Your Most Active Users
```python
from database import SessionLocal
from models import User

db = SessionLocal()
active_users = db.query(User).order_by(User.updated_at.desc()).limit(10).all()

for user in active_users:
    print(f"{user.display_name}: {user.updated_at}")

db.close()
```

### 2. Count New Users This Week
```python
from database import SessionLocal
from models import User
from datetime import datetime, timedelta

db = SessionLocal()
week_ago = datetime.utcnow() - timedelta(days=7)
new_users = db.query(User).filter(User.created_at >= week_ago).count()

print(f"New users this week: {new_users}")
db.close()
```

### 3. Find User by Display Name
```python
from database import SessionLocal
from models import User

db = SessionLocal()
user = db.query(User).filter(User.display_name.like("%John%")).first()

if user:
    print(f"Found: {user.display_name} ({user.line_user_id})")

db.close()
```

## Database Maintenance

### Backup Your Database
```bash
# Create backup
cp line_bot.db line_bot.db.backup-$(date +%Y%m%d)

# Or use sqlite3 backup command
sqlite3 line_bot.db ".backup line_bot.db.backup"
```

### View Database Size
```bash
du -h line_bot.db
```

### Compact Database (if needed)
```bash
sqlite3 line_bot.db "VACUUM;"
```

## Troubleshooting

### Database File Not Created?
- Check that application started successfully
- Look for "Database tables created successfully" in console
- Verify file permissions on directory

### "Database is locked" Error?
- SQLite allows only one write at a time
- This is normal - the code handles it automatically
- If persistent, restart the application

### Missing User Data?
- Check console logs for LINE API errors
- User may have blocked the bot (profile fetch fails)
- Minimal record is created even if profile fetch fails

## Privacy & Security

### Secure Your Database
```bash
# Set restrictive permissions (owner read/write only)
chmod 600 line_bot.db
```

### What's NOT Stored
- Message content (not stored by default)
- Message history (not implemented yet)
- Payment information
- Private conversations

### Data Retention
- Users are stored indefinitely by default
- Implement your own cleanup policy based on needs
- Consider GDPR requirements for your region

## Disabling Database (If Needed)

If you want to temporarily disable database features:

1. Edit `main.py`
2. Comment out lines 107-155 (the database block)
3. Remove `db: Session = Depends(get_db)` from line 81
4. Restart the application

The bot will work normally, just without user persistence.

## Next Steps

Now that user data is being stored, you can:

1. **Build Analytics** - Track user growth, engagement
2. **Add Personalization** - Greet returning users differently
3. **Store Messages** - Add message history tracking
4. **User Preferences** - Store language/notification preferences

See `IMPLEMENTATION_SUMMARY.md` for more advanced features.

## Support

**Files to Check**:
- `database.py` - Database configuration
- `models.py` - User model definition
- `main.py` - Integration logic
- `IMPLEMENTATION_SUMMARY.md` - Full technical details

**Common Commands**:
```bash
# View database schema
sqlite3 line_bot.db ".schema users"

# Check SQLAlchemy version
.venv/bin/pip show sqlalchemy

# Run tests
.venv/bin/python test_database.py
```

---

**Quick Reference**: All user data is in the `users` table in `line_bot.db` SQLite file.
