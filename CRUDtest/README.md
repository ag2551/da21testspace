# Social Media Hub - Phase 1 Complete

A Django-based social media management platform with Wagtail CMS for headless content management and Django Ninja for async REST APIs.

## Phase 1 Implementation Status ✅

All 7 tasks from the PRD have been successfully implemented:

1. ✅ **Environment Setup** - Python 3.12 virtual environment with all dependencies
2. ✅ **Django 5 Project Structure** - Configured with SQLite database
3. ✅ **Wagtail CMS** - Headless mode configuration with admin at `/cms`
4. ✅ **Django Ninja API** - Auto-documented REST API at `/api/docs`
5. ✅ **Celery + Redis** - Background task queue configured
6. ✅ **Adapter Pattern Structure** - Base classes for Facebook, LinkedIn, LINE
7. ✅ **Pytest Infrastructure** - All tests passing

## Project Structure

```
CRUDtest/
├── config/                      # Django project settings
│   ├── settings.py             # Main configuration
│   ├── urls.py                 # URL routing
│   ├── celery.py               # Celery configuration
│   └── __init__.py             # Celery app initialization
│
├── apps/
│   ├── api/                    # Django Ninja REST API
│   │   ├── routes.py           # API endpoints
│   │   └── tests/              # API tests
│   │
│   ├── social/                 # Social media integrations
│   │   ├── tasks.py            # Celery background tasks
│   │   ├── adapters/           # Platform adapters (Adapter Pattern)
│   │   │   ├── base.py         # Abstract base class
│   │   │   ├── facebook.py     # Facebook Graph API
│   │   │   ├── linkedin.py     # LinkedIn REST API
│   │   │   └── line.py         # LINE Messaging API
│   │   └── tests/              # Social app tests
│   │
│   └── content/                # Wagtail CMS content
│       └── tests/              # Content app tests
│
├── core/                       # Shared utilities
│
├── tests/                      # Project-wide tests
│
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── conftest.py                 # Pytest fixtures
├── manage.py                   # Django CLI
├── verify_phase1.sh            # Verification script
└── db.sqlite3                  # SQLite database (dev)
```

## Quick Start

### 1. Activate Virtual Environment

```bash
source .venv/bin/activate
```

### 2. Run Verification Script

```bash
./verify_phase1.sh
```

This validates:
- Python version
- Installed dependencies
- Django configuration
- All tests passing
- File structure
- Database migrations

### 3. Start Development Server

```bash
python manage.py runserver
```

### 4. Access Admin Interfaces

**Credentials:** `admin` / `admin`

- **Django Admin:** http://localhost:8000/admin
- **Wagtail CMS:** http://localhost:8000/cms
- **API Documentation:** http://localhost:8000/api/docs
- **Health Check:** http://localhost:8000/api/health

### 5. Start Celery Worker (Optional)

```bash
# In a separate terminal
celery -A config worker --loglevel=info
```

## Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12.3 | Runtime environment |
| Django | 5.0 | Web framework |
| Wagtail | 6.3 | Headless CMS |
| Django Ninja | 1.3.0 | Async REST API framework |
| Celery | 5.4.0 | Background task queue |
| Redis | 5.0.0 | Message broker |
| Pytest | 8.3.0 | Testing framework |
| SQLite | 3.x | Development database |

## Key Features Implemented

### 1. Django Ninja REST API

- **Health Check Endpoint:** `/api/health`
- **Auto-generated OpenAPI docs:** `/api/docs`
- **Async request handling**
- **Pydantic schema validation**

Example health check:

```bash
curl http://localhost:8000/api/health
```

Response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "message": "Social Media Hub API is running"
}
```

### 2. Wagtail CMS (Headless Mode)

- Admin interface at `/cms`
- Frontend serving disabled
- Ready for headless content management
- Media file handling configured

### 3. Celery Background Tasks

Sample tasks created in `apps/social/tasks.py`:

- `test_celery_task` - Test task for verification
- `publish_to_platform` - Template for platform publishing

### 4. Adapter Pattern Architecture

Base adapter class in `apps/social/adapters/base.py` defines interface:

- `create_post()` - Create new post
- `update_post()` - Update existing post
- `delete_post()` - Delete post
- `get_post()` - Retrieve post details

Platform adapters ready for implementation:

- **FacebookAdapter** - Graph API v19.0
- **LinkedInAdapter** - REST API /rest/posts (2025)
- **LINEAdapter** - Messaging API multicast

### 5. Testing Infrastructure

- Pytest configured with Django integration
- Async test support enabled
- 2 health check tests passing
- Test fixtures for API clients

Run tests:

```bash
pytest -v
```

## Configuration

### Environment Variables

Create `.env` file for production:

```env
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com

# Database (Production)
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Social Media Credentials
FACEBOOK_PAGE_ACCESS_TOKEN=...
LINKEDIN_ACCESS_TOKEN=...
LINE_CHANNEL_ACCESS_TOKEN=...
```

### Database Strategy

- **Development:** SQLite (zero configuration)
- **Production:** PostgreSQL (required for performance)

Switch to PostgreSQL in settings.py when deploying.

## Testing

### Run All Tests

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest apps/api/tests/test_health.py -v
```

### Run with Coverage

```bash
pytest --cov=apps --cov-report=html
```

## Next Steps (Phase 2)

The foundation is complete. Phase 2 will implement:

1. **Database Models**
   - PostTransaction
   - SocialCredential
   - PlatformPublishRecord
   - LineAudience

2. **Platform Adapters**
   - Implement Facebook posting logic
   - Implement LinkedIn /rest/posts API
   - Implement LINE multicast API

3. **Wagtail Pages**
   - SocialPostPage model
   - StreamField configuration
   - Pydantic serialization

4. **API Endpoints**
   - POST /api/posts/publish
   - GET /api/posts/{uuid}
   - PUT /api/posts/{uuid}
   - DELETE /api/posts/{uuid}

5. **Background Publishing**
   - Celery task integration
   - Retry logic
   - Error handling

## Troubleshooting

### Celery Worker Not Starting

Ensure Redis is running:

```bash
redis-cli ping  # Should return PONG
```

### Tests Failing

Reset database:

```bash
python manage.py migrate --run-syncdb
```

### Import Errors

Reinstall dependencies:

```bash
pip install -r requirements.txt --upgrade
```

## Documentation

- [INITIAL.md](./INITIAL.md) - Full project specification
- [PRD](./PRPs/PRD/Social_Media_Hub_PRD.md) - Phase 1 PRD
- [CLAUDE.md](./CLAUDE.md) - Project guidelines

## License

Internal project - All rights reserved

## Credits

Built with Django 5, Wagtail 6.3, and Django Ninja 1.3.0
