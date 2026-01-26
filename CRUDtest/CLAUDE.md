# CLAUDE.md - Project Context & Guidelines

## Project Overview
**Social Media Hub**: A headless CMS (Wagtail) and Async API Gateway (Django Ninja) to manage and publish content to LinkedIn, Facebook, and LINE.
- **Core Philosophy**: Database-first. The local DB is the "Single Source of Truth".
- **LINE Strategy**: LINE history is read from local DB. Updates are handled via "Unsend + Resend".

## Tech Stack
- **Language**: Python 3.10+
- **Framework**: Django 5.x
- **CMS**: Wagtail 6.x (Headless mode)
- **API**: Django Ninja (Async, Pydantic v2)
- **Database**: PostgreSQL (Production) / SQLite (Dev)
- **Task Queue**: Celery + Redis (for async broadcasting)
- **Testing**: Pytest

## Architecture Guidelines

### 1. Adapter Pattern (Crucial)
Do not put platform-specific logic in views or models. Use Adapters.
- Location: `apps/social/adapters/`
- Interface: `BaseProvider` (create, update, delete)
- Implementations: `LineProvider`, `FacebookProvider`, `LinkedInProvider`

### 2. Async & Sync Handling
- **API Views (`api.py`)**: Must be `async def`.
- **Wagtail ORM**: Wagtail is mostly sync. When accessing Wagtail Page models from Async Ninja views, ALWAYS use `asgiref.sync.sync_to_async`.
  ```python
  # Correct way to fetch Wagtail page in Ninja
  from asgiref.sync import sync_to_async
  page = await sync_to_async(BlogPage.objects.get)(id=post_id)

### 3. Data Models
- **Wagtail Pages**: Define content structure and editing UI.
- **`PostTransaction`**: The execution log. Links a Wagtail Page to a specific platform (e.g., "Page ID 5 posted to LINE at 10:00").
- **`LineAudience`**: Stores LINE user profiles from webhooks.

## Common Commands

### Environment
- Activate venv: `source .venv/bin/activate`
- Install deps: `pip install -r requirements.txt`

### Server Management
- Run Server (Dev): `python manage.py runserver`
- Start Celery Worker: `celery -A core worker -l info`
- Start Celery Beat: `celery -A core beat -l info`

### Database & Migrations
- Make migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`
- Create Superuser: `python manage.py createsuperuser`

### Testing
- Run all tests: `pytest`
- Run specific test: `pytest apps/social/tests/test_line_adapter.py`

## Coding Standards
- **Style**: PEP 8. Use `Black` for formatting.
- **Imports**: Sort imports with `isort`.
- **Typing**: Strict type hinting is required (used by Pydantic).
- **Docstrings**: Google Style docstrings for complex logic.
- **Error Handling**: Use `HttpError` from Django Ninja for API exceptions.

## Important constraints
1. **LINE Update**: If `PostTransaction` is > 24 hours old, raise `TimeLimitExceeded`. If < 24h, call Unsend -> Push.
2. **Wagtail API**: We are NOT using the built-in Wagtail API v2. We are building custom endpoints with Django Ninja to expose specific data structures.

## Project Structure
```text
root/
├── core/                # Project settings (wsgi, asgi, celary)
├── apps/
│   ├── content/         # Wagtail Page definitions
│   ├── social/          # Social Media Logic
│   │   ├── adapters/    # The Adapter Pattern implementations
│   │   ├── models.py    # PostTransaction, LineAudience
│   │   └── tasks.py     # Celery tasks
│   └── api/             # Django Ninja endpoints (Controllers)
├── manage.py
└── requirements.txt