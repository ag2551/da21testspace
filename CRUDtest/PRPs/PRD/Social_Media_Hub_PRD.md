# Product Requirement Document (PRD)
## Social Media Hub - Phase 1: Project Initialization

**Document Version**: 1.0
**Created**: 2026-01-27
**Based On**: INITIAL.md (Version 2.0)
**Target Phase**: Phase 1 (Week 1) - Project Initialization

---

## Executive Summary

This PRD defines the implementation plan for **Phase 1** of the Social Media Hub project: establishing the foundational Django 5 + Wagtail + Django Ninja infrastructure. This phase creates the skeleton upon which all subsequent features (Phase 2-5) will be built.

**Goal**: Create a fully functional development environment with:
- Django 5 project structure
- Wagtail CMS in headless mode
- Django Ninja async API framework
- Celery + Redis task queue
- SQLite database (development)
- Base app structure following the Adapter Pattern

**Success Metrics**:
- ✅ Django admin accessible at `/admin`
- ✅ Wagtail admin accessible at `/cms`
- ✅ API documentation at `/api/docs`
- ✅ Celery worker can execute test tasks
- ✅ All tests pass

---

## Table of Contents

1. [User Stories](#user-stories)
2. [Technical Architecture](#technical-architecture)
3. [Implementation Plan](#implementation-plan)
4. [File Structure](#file-structure)
5. [API Specifications](#api-specifications)
6. [Database Schema](#database-schema)
7. [Configuration & Environment](#configuration--environment)
8. [Testing Strategy](#testing-strategy)
9. [Verification Steps](#verification-steps)
10. [Dependencies](#dependencies)

---

## 1. User Stories

### US-1.1: As a Developer, I need a Django project structure
**Acceptance Criteria**:
- Django 5.x project created with proper settings module
- Project follows Django best practices (separate settings for dev/prod)
- All required apps installed and configured
- Database migrations applied successfully

**Why**: Establishes the foundation for all subsequent development

---

### US-1.2: As a Content Creator, I need Wagtail CMS access
**Acceptance Criteria**:
- Wagtail admin accessible at `/cms`
- Can create a superuser account
- Wagtail homepage exists and is customizable
- Wagtail is configured in headless mode (API-first)

**Why**: Enables content management capabilities from day one

---

### US-1.3: As a Frontend Developer, I need API documentation
**Acceptance Criteria**:
- Django Ninja installed and configured
- OpenAPI documentation auto-generated at `/api/docs`
- At least one test endpoint exists and is documented
- API returns proper JSON responses

**Why**: Ensures API-first development and enables frontend integration

---

### US-1.4: As a System Architect, I need async task processing
**Acceptance Criteria**:
- Celery configured with Redis broker
- Can execute a test task asynchronously
- Celery worker logs are visible
- Celery Beat (scheduler) is configured

**Why**: Required for async publishing to social media platforms

---

### US-1.5: As a Developer, I need a clear project structure
**Acceptance Criteria**:
- Apps organized following the Adapter Pattern
- Clear separation: `core/`, `apps/content/`, `apps/social/`, `apps/api/`
- Each app has proper `__init__.py`, `models.py`, `views.py`, etc.
- Configuration files are well-documented

**Why**: Maintainable codebase that scales with feature additions

---

## 2. Technical Architecture

### 2.1 System Components

```
┌─────────────────────────────────────────────────────────┐
│                   Phase 1 Architecture                   │
└─────────────────────────────────────────────────────────┘

┌──────────────────┐      ┌──────────────────┐
│   Wagtail CMS    │◄────►│   Django ORM     │
│   (Headless)     │      │   (SQLite Dev)   │
└──────────────────┘      └──────────────────┘
         │                         │
         │                         │
         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐
│  Django Ninja    │      │  Celery Workers  │
│  (Async API)     │      │  (Redis Broker)  │
└──────────────────┘      └──────────────────┘
         │                         │
         └────────┬────────────────┘
                  ▼
         ┌──────────────────┐
         │  Django Project  │
         │  (Core Settings) │
         └──────────────────┘
```

### 2.2 Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Backend** | Django | 5.0 | Web framework, ORM, admin |
| **CMS** | Wagtail | 6.3+ | Content management |
| **API** | Django Ninja | 1.3+ | Async REST API with Pydantic |
| **Database** | SQLite | 3.x | Development database |
| **Task Queue** | Celery | 5.4+ | Async task processing |
| **Broker** | Redis | 7.x | Celery message broker |
| **Python** | Python | 3.11+ | Runtime environment |

### 2.3 Architectural Patterns

**Adapter Pattern** (from CLAUDE.md):
- Location: `apps/social/adapters/`
- Interface: `BaseProvider` (create, update, delete)
- Future implementations: `LineProvider`, `FacebookProvider`, `LinkedInProvider`

**Async/Sync Boundary**:
- API views (`api.py`): `async def` functions
- Wagtail ORM access: Use `sync_to_async` wrapper
- Celery tasks: Synchronous functions (Celery handles async execution)

---

## 3. Implementation Plan

### 3.1 Step-by-Step Tasks

#### Task 1: Environment Setup (30 minutes)

**Goal**: Create Python virtual environment and install dependencies

**Steps**:
1. Create virtual environment:
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Create `requirements.txt`:
   ```txt
   # Core Framework
   Django==5.0

   # CMS
   wagtail==6.3

   # API Framework
   django-ninja==1.3.0

   # Async Support
   asgiref==3.8.1

   # Task Queue
   celery==5.4.0
   redis==5.0.0

   # Security
   django-cryptography==1.1

   # HTTP Client
   httpx==0.27.0

   # Database (Production - optional for Phase 1)
   psycopg2-binary==2.9.9
   dj-database-url==2.2.0

   # Development Tools
   pytest==8.3.0
   pytest-django==4.9.0
   pytest-asyncio==0.24.0
   black==24.8.0
   isort==5.13.0

   # Environment Management
   python-dotenv==1.0.0
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

**Verification**:
- `python --version` shows 3.11+
- `pip list` shows all packages installed
- No errors during installation

---

#### Task 2: Django Project Initialization (20 minutes)

**Goal**: Create base Django project structure

**Steps**:
1. Create Django project:
   ```bash
   django-admin startproject config .
   ```

2. Create core apps:
   ```bash
   python manage.py startapp content
   python manage.py startapp social
   python manage.py startapp api

   # Move apps into apps/ directory
   mkdir apps
   mv content social api apps/
   ```

3. Update `config/settings.py`:
   ```python
   import os
   from pathlib import Path

   BASE_DIR = Path(__file__).resolve().parent.parent

   # Add apps directory to Python path
   import sys
   sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

   INSTALLED_APPS = [
       # Django defaults
       'django.contrib.admin',
       'django.contrib.auth',
       'django.contrib.contenttypes',
       'django.contrib.sessions',
       'django.contrib.messages',
       'django.contrib.staticfiles',

       # Third-party apps
       'wagtail.contrib.forms',
       'wagtail.contrib.redirects',
       'wagtail.embeds',
       'wagtail.sites',
       'wagtail.users',
       'wagtail.snippets',
       'wagtail.documents',
       'wagtail.images',
       'wagtail.search',
       'wagtail.admin',
       'wagtail',
       'modelcluster',
       'taggit',

       # Custom apps
       'content',
       'social',
       'api',
   ]

   # Middleware
   MIDDLEWARE = [
       'django.middleware.security.SecurityMiddleware',
       'django.contrib.sessions.middleware.SessionMiddleware',
       'django.middleware.common.CommonMiddleware',
       'django.middleware.csrf.CsrfViewMiddleware',
       'django.contrib.auth.middleware.AuthenticationMiddleware',
       'django.contrib.messages.middleware.MessageMiddleware',
       'django.middleware.clickjacking.XFrameOptionsMiddleware',
       'wagtail.contrib.redirects.middleware.RedirectMiddleware',
   ]

   # Database (SQLite for development)
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }

   # Wagtail settings
   WAGTAIL_SITE_NAME = 'Social Media Hub'
   WAGTAILADMIN_BASE_URL = 'http://localhost:8000'
   ```

**Files Created**:
- `config/settings.py` (modified)
- `config/urls.py` (modified)
- `config/wsgi.py`
- `config/asgi.py`
- `apps/content/`, `apps/social/`, `apps/api/`

**Verification**:
```bash
python manage.py check
# Should output: System check identified no issues (0 silenced).
```

---

#### Task 3: Wagtail Configuration (30 minutes)

**Goal**: Set up Wagtail CMS in headless mode

**Steps**:

1. Update `config/urls.py`:
   ```python
   from django.contrib import admin
   from django.urls import path, include
   from wagtail.admin import urls as wagtailadmin_urls
   from wagtail import urls as wagtail_urls

   urlpatterns = [
       path('admin/', admin.site.urls),
       path('cms/', include(wagtailadmin_urls)),
       path('', include(wagtail_urls)),
   ]
   ```

2. Create Wagtail home page model in `apps/content/models.py`:
   ```python
   from django.db import models
   from wagtail.models import Page
   from wagtail.fields import RichTextField
   from wagtail.admin.panels import FieldPanel

   class HomePage(Page):
       """
       Wagtail home page.
       This is a placeholder for the CMS structure.
       """
       body = RichTextField(blank=True)

       content_panels = Page.content_panels + [
           FieldPanel('body'),
       ]

       class Meta:
           verbose_name = "Home Page"
   ```

3. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Create superuser:
   ```bash
   python manage.py createsuperuser
   # Username: admin
   # Email: admin@example.com
   # Password: (your secure password)
   ```

5. Create Wagtail site:
   ```bash
   python manage.py shell
   ```
   ```python
   from wagtail.models import Site, Page
   from content.models import HomePage

   # Get the root page
   root = Page.objects.get(id=1)

   # Create home page
   home = HomePage(title="Home", slug="home")
   root.add_child(instance=home)

   # Create site
   Site.objects.create(
       hostname='localhost',
       port=8000,
       root_page=home,
       is_default_site=True,
       site_name='Social Media Hub'
   )
   ```

**Verification**:
```bash
python manage.py runserver
# Visit: http://localhost:8000/cms
# Should see Wagtail login page
# Login with superuser credentials
```

---

#### Task 4: Django Ninja API Setup (30 minutes)

**Goal**: Configure async REST API with auto-documentation

**Steps**:

1. Create `apps/api/ninja_api.py`:
   ```python
   from ninja import NinjaAPI
   from typing import Dict

   # Create API instance with auto-documentation
   api = NinjaAPI(
       title="Social Media Hub API",
       version="1.0.0",
       description="Async REST API for cross-platform social media publishing",
       docs_url="/docs",
   )

   # Health check endpoint (test endpoint)
   @api.get("/health", tags=["System"])
   async def health_check(request) -> Dict[str, str]:
       """
       Health check endpoint.
       Returns system status.
       """
       return {
           "status": "healthy",
           "version": "1.0.0",
           "message": "Social Media Hub API is running"
       }

   # Placeholder for future endpoints
   @api.get("/ping", tags=["System"])
   async def ping(request) -> Dict[str, str]:
       """Simple ping endpoint for testing async functionality"""
       return {"message": "pong"}
   ```

2. Update `config/urls.py` to include API:
   ```python
   from django.contrib import admin
   from django.urls import path, include
   from wagtail.admin import urls as wagtailadmin_urls
   from wagtail import urls as wagtail_urls
   from api.ninja_api import api

   urlpatterns = [
       path('admin/', admin.site.urls),
       path('cms/', include(wagtailadmin_urls)),
       path('api/', api.urls),  # Django Ninja API
       path('', include(wagtail_urls)),
   ]
   ```

3. Create `apps/api/__init__.py` (empty file for Python module)

**Verification**:
```bash
python manage.py runserver
# Visit: http://localhost:8000/api/docs
# Should see OpenAPI/Swagger documentation
# Test /api/health endpoint - should return JSON response
```

---

#### Task 5: Celery Configuration (45 minutes)

**Goal**: Set up async task queue with Redis broker

**Steps**:

1. Install and start Redis:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install redis-server
   sudo systemctl start redis

   # On macOS
   brew install redis
   brew services start redis

   # Verify Redis is running
   redis-cli ping
   # Should return: PONG
   ```

2. Create `config/celery.py`:
   ```python
   import os
   from celery import Celery

   # Set default Django settings module
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

   # Create Celery app
   app = Celery('social_media_hub')

   # Load config from Django settings (namespace='CELERY')
   app.config_from_object('django.conf:settings', namespace='CELERY')

   # Auto-discover tasks in all installed apps
   app.autodiscover_tasks()

   @app.task(bind=True)
   def debug_task(self):
       """Debug task for testing Celery setup"""
       print(f'Request: {self.request!r}')
   ```

3. Update `config/__init__.py`:
   ```python
   # This will make sure the app is always imported when
   # Django starts so that shared_task will use this app.
   from .celery import app as celery_app

   __all__ = ('celery_app',)
   ```

4. Add Celery settings to `config/settings.py`:
   ```python
   # Celery Configuration
   CELERY_BROKER_URL = 'redis://localhost:6379/0'
   CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
   CELERY_ACCEPT_CONTENT = ['json']
   CELERY_TASK_SERIALIZER = 'json'
   CELERY_RESULT_SERIALIZER = 'json'
   CELERY_TIMEZONE = 'UTC'
   CELERY_TASK_TRACK_STARTED = True
   CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
   ```

5. Create test task in `apps/social/tasks.py`:
   ```python
   from celery import shared_task
   import time

   @shared_task
   def test_task(duration: int = 5):
       """
       Test Celery task that simulates a long-running operation.

       Args:
           duration: Seconds to sleep

       Returns:
           Success message
       """
       print(f"Starting test task, will sleep for {duration} seconds...")
       time.sleep(duration)
       print("Test task completed!")
       return f"Task completed after {duration} seconds"

   @shared_task
   def add(x: int, y: int) -> int:
       """Simple addition task for testing"""
       return x + y
   ```

6. Create Celery Beat schedule (optional - for future scheduled tasks):
   ```python
   # In config/settings.py
   from celery.schedules import crontab

   CELERY_BEAT_SCHEDULE = {
       # Example: Run test task every 5 minutes
       'test-task-every-5-minutes': {
           'task': 'social.tasks.test_task',
           'schedule': crontab(minute='*/5'),
           'args': (3,)
       },
   }
   ```

**Verification**:
```bash
# Terminal 1: Start Celery worker
celery -A config worker -l info

# Terminal 2: Test task execution
python manage.py shell
```
```python
from social.tasks import add, test_task

# Synchronous execution (for testing)
result = add(4, 5)
print(result)  # Should print: 9

# Async execution
task = add.delay(10, 20)
print(task.id)  # Task ID
print(task.status)  # PENDING, SUCCESS, etc.
print(task.result)  # 30 (when completed)

# Long-running task
long_task = test_task.delay(5)
print(long_task.status)  # Check status
```

---

#### Task 6: Project Structure Organization (20 minutes)

**Goal**: Create proper directory structure following Adapter Pattern

**Steps**:

1. Create directory structure:
   ```bash
   mkdir -p apps/social/adapters
   mkdir -p apps/social/tests
   mkdir -p apps/content/tests
   mkdir -p apps/api/tests
   mkdir -p static
   mkdir -p media
   mkdir -p logs
   ```

2. Create placeholder files:

   **`apps/social/adapters/__init__.py`**:
   ```python
   """
   Social Media Adapters (Adapter Pattern).

   This package contains platform-specific adapters for:
   - Facebook (FacebookProvider)
   - LinkedIn (LinkedInProvider)
   - LINE (LineProvider)

   Each adapter implements the BaseProvider interface.
   """
   ```

   **`apps/social/adapters/base.py`**:
   ```python
   from abc import ABC, abstractmethod
   from typing import Optional, Dict, Any

   class BaseProvider(ABC):
       """
       Abstract base class for social media platform providers.

       All platform adapters must implement these methods.
       """

       @abstractmethod
       async def create_post(
           self,
           content: str,
           media: Optional[bytes] = None,
           **kwargs
       ) -> Dict[str, Any]:
           """
           Create a new post on the platform.

           Args:
               content: Post text content
               media: Optional image/video bytes
               **kwargs: Platform-specific parameters

           Returns:
               Dict with post_id and platform-specific data
           """
           pass

       @abstractmethod
       async def update_post(
           self,
           post_id: str,
           content: str,
           **kwargs
       ) -> Dict[str, Any]:
           """Update an existing post"""
           pass

       @abstractmethod
       async def delete_post(self, post_id: str) -> bool:
           """Delete a post"""
           pass

       @abstractmethod
       async def validate_credentials(self) -> bool:
           """Validate platform credentials"""
           pass
   ```

3. Create `.env.example`:
   ```env
   # Django Settings
   SECRET_KEY=your-secret-key-here-change-in-production
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1

   # Database (SQLite for development - no config needed)
   # For production PostgreSQL:
   # DATABASE_URL=postgresql://user:password@localhost:5432/socialhub

   # Redis
   REDIS_URL=redis://localhost:6379/0

   # Facebook Graph API
   FACEBOOK_APP_ID=your-app-id
   FACEBOOK_APP_SECRET=your-app-secret

   # LinkedIn API
   LINKEDIN_CLIENT_ID=your-client-id
   LINKEDIN_CLIENT_SECRET=your-client-secret

   # LINE Messaging API
   LINE_CHANNEL_SECRET=your-channel-secret
   LINE_CHANNEL_ACCESS_TOKEN=your-access-token
   ```

4. Create `.gitignore`:
   ```gitignore
   # Python
   __pycache__/
   *.py[cod]
   *$py.class
   *.so
   .Python
   .venv/
   venv/
   env/

   # Django
   *.log
   db.sqlite3
   db.sqlite3-journal
   /media
   /static

   # Environment
   .env
   .env.local

   # IDE
   .vscode/
   .idea/
   *.swp
   *.swo

   # Celery
   celerybeat-schedule
   celerybeat.pid

   # Testing
   .pytest_cache/
   .coverage
   htmlcov/

   # macOS
   .DS_Store
   ```

**Final Directory Structure**:
```
CRUDtest/
├── config/                 # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py
├── apps/
│   ├── content/           # Wagtail pages & content models
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── admin.py
│   │   └── tests/
│   ├── social/            # Social media logic
│   │   ├── __init__.py
│   │   ├── models.py      # PostTransaction, SocialCredential, etc.
│   │   ├── tasks.py       # Celery tasks
│   │   ├── adapters/      # Adapter Pattern implementations
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── facebook.py (future)
│   │   │   ├── linkedin.py (future)
│   │   │   └── line.py (future)
│   │   └── tests/
│   └── api/               # Django Ninja API endpoints
│       ├── __init__.py
│       ├── ninja_api.py
│       └── tests/
├── static/                # Static files (CSS, JS, images)
├── media/                 # User-uploaded media
├── logs/                  # Application logs
├── PRPs/                  # Product requirements
│   └── PRD/
│       └── Social_Media_Hub_PRD.md
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── CLAUDE.md
└── INITIAL.md
```

---

#### Task 7: Testing Setup (30 minutes)

**Goal**: Configure pytest and create initial tests

**Steps**:

1. Create `pytest.ini`:
   ```ini
   [pytest]
   DJANGO_SETTINGS_MODULE = config.settings
   python_files = test_*.py
   python_classes = Test*
   python_functions = test_*
   addopts = -v --tb=short --strict-markers
   testpaths = apps
   markers =
       unit: Unit tests
       integration: Integration tests
       async: Async tests
   ```

2. Create `apps/conftest.py`:
   ```python
   import pytest
   from django.conf import settings

   @pytest.fixture(scope='session')
   def django_db_setup():
       """Override database for tests"""
       settings.DATABASES['default'] = {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': ':memory:',
       }
   ```

3. Create test files:

   **`apps/api/tests/test_ninja_api.py`**:
   ```python
   import pytest
   from django.test import Client

   @pytest.mark.django_db
   def test_health_endpoint():
       """Test health check endpoint"""
       client = Client()
       response = client.get('/api/health')

       assert response.status_code == 200
       data = response.json()
       assert data['status'] == 'healthy'
       assert data['version'] == '1.0.0'

   @pytest.mark.django_db
   def test_ping_endpoint():
       """Test ping endpoint"""
       client = Client()
       response = client.get('/api/ping')

       assert response.status_code == 200
       data = response.json()
       assert data['message'] == 'pong'
   ```

   **`apps/social/tests/test_tasks.py`**:
   ```python
   import pytest
   from social.tasks import add, test_task

   @pytest.mark.unit
   def test_add_task():
       """Test simple addition task"""
       result = add(5, 10)
       assert result == 15

   @pytest.mark.unit
   def test_add_task_negative():
       """Test addition with negative numbers"""
       result = add(-5, 10)
       assert result == 5
   ```

4. Run tests:
   ```bash
   pytest
   # Should see all tests passing
   ```

**Verification**:
```bash
pytest -v
# Output should show:
# apps/api/tests/test_ninja_api.py::test_health_endpoint PASSED
# apps/api/tests/test_ninja_api.py::test_ping_endpoint PASSED
# apps/social/tests/test_tasks.py::test_add_task PASSED
# apps/social/tests/test_tasks.py::test_add_task_negative PASSED
```

---

## 4. File Structure

### 4.1 Complete File Tree

```
CRUDtest/
├── config/
│   ├── __init__.py              # Imports celery app
│   ├── settings.py              # Django settings (updated)
│   ├── urls.py                  # URL configuration (updated)
│   ├── wsgi.py                  # WSGI entry point
│   ├── asgi.py                  # ASGI entry point
│   └── celery.py                # NEW: Celery configuration
│
├── apps/
│   ├── content/
│   │   ├── __init__.py
│   │   ├── models.py            # NEW: HomePage model
│   │   ├── admin.py
│   │   ├── apps.py
│   │   └── tests/
│   │       └── __init__.py
│   │
│   ├── social/
│   │   ├── __init__.py
│   │   ├── models.py            # Empty (Phase 2)
│   │   ├── tasks.py             # NEW: Celery tasks
│   │   ├── adapters/
│   │   │   ├── __init__.py      # NEW: Module docstring
│   │   │   └── base.py          # NEW: BaseProvider interface
│   │   └── tests/
│   │       ├── __init__.py
│   │       └── test_tasks.py    # NEW: Task tests
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── ninja_api.py         # NEW: Django Ninja API
│   │   └── tests/
│   │       ├── __init__.py
│   │       └── test_ninja_api.py # NEW: API tests
│   │
│   └── conftest.py              # NEW: Pytest configuration
│
├── static/                      # NEW: Static files directory
├── media/                       # NEW: Media uploads directory
├── logs/                        # NEW: Log files directory
│
├── PRPs/
│   └── PRD/
│       └── Social_Media_Hub_PRD.md  # THIS FILE
│
├── manage.py                    # Django management script
├── requirements.txt             # NEW: Python dependencies
├── pytest.ini                   # NEW: Pytest configuration
├── .env.example                 # NEW: Environment template
├── .gitignore                   # NEW: Git ignore rules
├── CLAUDE.md                    # Existing: Project guidelines
└── INITIAL.md                   # Existing: Initial requirements
```

### 4.2 Files to Create

**New Files (17 total)**:
1. `config/celery.py`
2. `apps/content/models.py` (updated)
3. `apps/social/tasks.py`
4. `apps/social/adapters/__init__.py`
5. `apps/social/adapters/base.py`
6. `apps/social/tests/__init__.py`
7. `apps/social/tests/test_tasks.py`
8. `apps/api/ninja_api.py`
9. `apps/api/tests/__init__.py`
10. `apps/api/tests/test_ninja_api.py`
11. `apps/conftest.py`
12. `requirements.txt`
13. `pytest.ini`
14. `.env.example`
15. `.gitignore`
16. `PRPs/PRD/Social_Media_Hub_PRD.md`
17. Directories: `static/`, `media/`, `logs/`

**Modified Files (3 total)**:
1. `config/__init__.py` (add celery import)
2. `config/settings.py` (add Wagtail, Celery, apps)
3. `config/urls.py` (add Wagtail and API routes)

---

## 5. API Specifications

### 5.1 Phase 1 Endpoints

#### GET `/api/health`
**Purpose**: Health check endpoint
**Method**: GET
**Authentication**: None
**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "message": "Social Media Hub API is running"
}
```

#### GET `/api/ping`
**Purpose**: Simple async test endpoint
**Method**: GET
**Authentication**: None
**Response**:
```json
{
  "message": "pong"
}
```

#### GET `/api/docs`
**Purpose**: OpenAPI documentation (Swagger UI)
**Method**: GET
**Authentication**: None
**Response**: HTML page with interactive API documentation

### 5.2 Future Endpoints (Phase 2+)

These will be implemented in later phases:
- `POST /api/posts/` - Create new post
- `GET /api/posts/{uuid}/` - Get post status
- `PUT /api/posts/{uuid}/` - Update post
- `DELETE /api/posts/{uuid}/` - Delete post
- `POST /api/webhooks/line/` - LINE webhook receiver
- `GET /api/credentials/` - List social credentials
- `POST /api/credentials/` - Add new credential

---

## 6. Database Schema

### 6.1 Phase 1 Models

**Wagtail Models** (auto-created):
- `wagtailcore_Page` - Base page model
- `content_HomePage` - Custom home page
- `wagtailcore_Site` - Site configuration

**Custom Models** (Phase 2):
- `social_PostTransaction` - NOT CREATED IN PHASE 1
- `social_SocialCredential` - NOT CREATED IN PHASE 1
- `social_PlatformPublishRecord` - NOT CREATED IN PHASE 1
- `social_LineAudience` - NOT CREATED IN PHASE 1

### 6.2 Migrations

Phase 1 migrations:
```bash
python manage.py makemigrations content
python manage.py migrate
```

Expected migrations:
- `0001_initial.py` - Creates HomePage model
- Wagtail core migrations (auto-applied)

---

## 7. Configuration & Environment

### 7.1 Environment Variables

**Required for Phase 1**:
```env
SECRET_KEY=your-django-secret-key
DEBUG=True
REDIS_URL=redis://localhost:6379/0
```

**Optional (for future phases)**:
```env
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=
LINE_CHANNEL_SECRET=
LINE_CHANNEL_ACCESS_TOKEN=
```

### 7.2 Django Settings Updates

**New settings added to `config/settings.py`**:

```python
# Wagtail Configuration
INSTALLED_APPS += [
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',
    'modelcluster',
    'taggit',
]

WAGTAIL_SITE_NAME = 'Social Media Hub'
WAGTAILADMIN_BASE_URL = 'http://localhost:8000'

# Celery Configuration
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Static/Media Files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

---

## 8. Testing Strategy

### 8.1 Test Categories

**Unit Tests**:
- Test individual functions and methods
- Mock external dependencies
- Fast execution (<100ms per test)

**Integration Tests**:
- Test component interactions
- Use test database
- Moderate execution time

**Async Tests**:
- Test async functions and coroutines
- Use pytest-asyncio
- Verify async behavior

### 8.2 Test Coverage Goals

Phase 1 targets:
- **API Endpoints**: 100% coverage
- **Celery Tasks**: 100% coverage
- **Models**: N/A (no custom models yet)
- **Adapters**: Interface defined, no implementation yet

### 8.3 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps --cov-report=html

# Run specific test file
pytest apps/api/tests/test_ninja_api.py

# Run specific test
pytest apps/api/tests/test_ninja_api.py::test_health_endpoint

# Run only unit tests
pytest -m unit

# Run only async tests
pytest -m async
```

---

## 9. Verification Steps

### 9.1 Automated Verification Checklist

Run these commands to verify Phase 1 completion:

#### ✅ Step 1: Environment Setup
```bash
# Verify Python version
python --version
# Expected: Python 3.11.x or higher

# Verify virtual environment
which python
# Expected: /path/to/CRUDtest/.venv/bin/python

# Verify dependencies
pip list | grep -E "Django|wagtail|django-ninja|celery|redis"
# Expected: All packages listed with correct versions
```

#### ✅ Step 2: Django Project
```bash
# Django system check
python manage.py check
# Expected: System check identified no issues (0 silenced).

# Check migrations
python manage.py showmigrations
# Expected: All migrations shown, some applied

# Create superuser (if not done)
python manage.py createsuperuser
```

#### ✅ Step 3: Wagtail CMS
```bash
# Start server
python manage.py runserver

# Open browser and test:
# http://localhost:8000/cms/
# Expected: Wagtail login page

# Login with superuser credentials
# Expected: Wagtail dashboard
```

#### ✅ Step 4: Django Ninja API
```bash
# Test API endpoints
curl http://localhost:8000/api/health
# Expected: {"status":"healthy","version":"1.0.0",...}

curl http://localhost:8000/api/ping
# Expected: {"message":"pong"}

# Open browser:
# http://localhost:8000/api/docs
# Expected: Swagger UI with API documentation
```

#### ✅ Step 5: Celery Worker
```bash
# Terminal 1: Start Redis
redis-server
# Expected: Redis server running on port 6379

# Terminal 2: Start Celery worker
celery -A config worker -l info
# Expected: Worker starts, shows "ready" message

# Terminal 3: Test task execution
python manage.py shell
>>> from social.tasks import add
>>> result = add.delay(10, 20)
>>> result.status
# Expected: 'SUCCESS'
>>> result.result
# Expected: 30
```

#### ✅ Step 6: Tests
```bash
# Run all tests
pytest -v
# Expected: All tests pass (4 tests minimum)

# Check test coverage
pytest --cov=apps --cov-report=term
# Expected: Coverage report showing >80% for tested modules
```

---

### 9.2 Manual Verification Checklist

| Check | Expected Result | Status |
|-------|----------------|--------|
| Django admin accessible at `/admin` | Login page appears | ⬜ |
| Wagtail admin accessible at `/cms` | Wagtail dashboard appears | ⬜ |
| API docs accessible at `/api/docs` | Swagger UI appears | ⬜ |
| `/api/health` returns JSON | `{"status": "healthy"}` | ⬜ |
| Celery worker starts without errors | Worker shows "ready" | ⬜ |
| Celery can execute tasks | Task completes successfully | ⬜ |
| All tests pass | `pytest` shows all green | ⬜ |
| Directory structure matches spec | All required directories exist | ⬜ |
| `.env.example` file exists | Template is complete | ⬜ |
| `.gitignore` file exists | Covers all sensitive files | ⬜ |

---

### 9.3 Integration Test

**End-to-End Flow Test**:

1. Create content in Wagtail:
   - Login to `/cms`
   - Navigate to Pages
   - Create a new page under Home
   - Publish the page

2. Test API:
   - Visit `/api/docs`
   - Execute `/api/health` endpoint
   - Verify JSON response

3. Test Celery:
   - Run Python shell
   - Execute async task
   - Verify task completion

4. Run full test suite:
   ```bash
   pytest --cov=apps --cov-report=html
   open htmlcov/index.html  # View coverage report
   ```

**Success Criteria**:
- All manual checks pass ✅
- All automated tests pass ✅
- No errors in Django logs ✅
- No errors in Celery logs ✅
- Coverage report shows >80% for implemented features ✅

---

## 10. Dependencies

### 10.1 Python Dependencies

**Complete `requirements.txt`**:

```txt
# Core Framework (Django 5)
Django==5.0

# CMS (Wagtail)
wagtail==6.3

# API Framework (Django Ninja)
django-ninja==1.3.0
pydantic==2.9.0

# Async Support
asgiref==3.8.1

# Task Queue (Celery + Redis)
celery==5.4.0
redis==5.0.0

# Security
django-cryptography==1.1

# HTTP Client (for platform API calls)
httpx==0.27.0

# Database (Production)
psycopg2-binary==2.9.9
dj-database-url==2.2.0

# Development Tools
pytest==8.3.0
pytest-django==4.9.0
pytest-asyncio==0.24.0
pytest-cov==5.0.0
black==24.8.0
isort==5.13.0
flake8==7.1.0

# Environment Management
python-dotenv==1.0.0

# Wagtail Dependencies (auto-installed)
# - modelcluster
# - taggit
# - Pillow (image handling)
# - beautifulsoup4
```

### 10.2 System Dependencies

**Required Services**:
- Python 3.11+
- Redis 7.x (for Celery broker)
- SQLite 3.x (included with Python)

**Optional (for production)**:
- PostgreSQL 14+
- Nginx (for static file serving)
- Supervisor (for process management)

### 10.3 Installation Order

```bash
# 1. Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# 2. Upgrade pip
pip install --upgrade pip

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Redis (system package)
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis

# 5. Verify installations
python --version    # 3.11+
django-admin --version  # 5.0.x
redis-cli ping     # PONG
```

---

## 11. Troubleshooting

### 11.1 Common Issues

#### Issue: "No module named 'config'"
**Solution**: Ensure you're in the project root and virtual environment is activated:
```bash
cd /path/to/CRUDtest
source .venv/bin/activate
python manage.py check
```

#### Issue: "Redis connection refused"
**Solution**: Start Redis server:
```bash
# Ubuntu/Debian
sudo systemctl start redis

# macOS
brew services start redis

# Verify
redis-cli ping
```

#### Issue: "ModuleNotFoundError: No module named 'wagtail'"
**Solution**: Reinstall dependencies:
```bash
pip install -r requirements.txt
```

#### Issue: Celery worker won't start
**Solution**: Check Redis connection and app name:
```bash
# Test Redis
redis-cli ping

# Start worker with debug
celery -A config worker -l debug
```

#### Issue: Tests failing with database errors
**Solution**: Run migrations:
```bash
python manage.py migrate
pytest
```

### 11.2 Debug Commands

```bash
# Check Django configuration
python manage.py check

# Show migrations status
python manage.py showmigrations

# Test database connection
python manage.py dbshell

# Test Celery configuration
celery -A config inspect stats

# View Celery registered tasks
celery -A config inspect registered

# Check Redis connection
redis-cli ping
redis-cli info
```

---

## 12. Next Steps (Post-Phase 1)

After Phase 1 completion, proceed to:

### Phase 2: Core Models & Wagtail Integration (Week 2)
**Tasks**:
- Create `PostTransaction` model
- Create `SocialCredential` model with encryption
- Create `PlatformPublishRecord` model
- Create `LineAudience` model
- Build `SocialPostPage` with StreamField
- Implement Pydantic schemas for Wagtail serialization

### Phase 3: LINE Integration (Week 3-4)
**Tasks**:
- Implement `LineAdapter` (following `BaseProvider` interface)
- Build webhook endpoint with signature verification
- Implement rate limiter (200 req/sec for multicast)
- Create `LineAudience` management

### Phase 4: Facebook & LinkedIn Adapters (Week 5-6)
**Tasks**:
- Implement `FacebookAdapter` with token refresh
- Implement `LinkedInAdapter` with `/rest/posts` API
- Test image upload workflows

### Phase 5: Unified Publishing & Dashboard (Week 7-8)
**Tasks**:
- Integrate all adapters
- Build unified publishing task
- Create status dashboard
- Implement scheduled publishing

---

## 13. Success Criteria Summary

### Phase 1 is considered **complete** when:

✅ **Environment**:
- Virtual environment created and activated
- All dependencies installed without errors
- Python 3.11+ verified

✅ **Django Project**:
- Django 5.0 project created
- Apps structure follows specification
- Migrations applied successfully
- Superuser created

✅ **Wagtail CMS**:
- Wagtail admin accessible at `/cms`
- Can login with superuser
- HomePage model exists
- Site configured

✅ **Django Ninja API**:
- API documentation at `/api/docs`
- Health check endpoint works
- Swagger UI displays correctly

✅ **Celery & Redis**:
- Redis server running
- Celery worker can start
- Test tasks execute successfully
- No connection errors

✅ **Testing**:
- All tests pass (minimum 4 tests)
- Test coverage >80% for implemented code
- `pytest` runs without errors

✅ **Documentation**:
- This PRD completed ✅
- `.env.example` created
- README updated (optional but recommended)

✅ **Code Quality**:
- Follows PEP 8 (validated with `black` and `flake8`)
- No critical security issues
- Proper error handling in place

---

## 14. Review & Approval

### 14.1 Review Checklist for Team

Before proceeding to Phase 2, verify:

- [ ] All tasks in Implementation Plan completed
- [ ] All files in File Structure created
- [ ] All verification steps passed
- [ ] No blockers or critical issues
- [ ] Documentation is up-to-date
- [ ] Code follows project standards (CLAUDE.md)
- [ ] All tests pass locally
- [ ] Git repository initialized (optional)
- [ ] Team has reviewed and approved

### 14.2 Sign-Off

**Developer**: ___________________ Date: ___________

**Tech Lead**: ___________________ Date: ___________

**Approved to proceed to Phase 2**: ☐ Yes ☐ No

**Notes**:
```
[Space for reviewer comments and concerns]
```

---

## Appendix A: Code Patterns from Example Projects

### A.1 FastAPI Pattern (from LINE_chat_id/main.py)

**Lifespan Management**:
```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global async_api_client, line_bot_api
    async_api_client = AsyncApiClient(configuration)
    line_bot_api = AsyncMessagingApi(async_api_client)
    yield
    # Shutdown
    await async_api_client.close()

app = FastAPI(lifespan=lifespan)
```

**Lessons for Django Ninja**:
- Use async context managers for client initialization
- Separate startup/shutdown logic
- Global clients for reuse across requests

### A.2 Webhook Signature Verification

**LINE Example Pattern**:
```python
from linebot.v3.webhook import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError

parser = WebhookParser(channel_secret)

try:
    events = parser.parse(body, signature)
except InvalidSignatureError:
    raise HTTPException(status_code=400, detail="Invalid signature")
```

**Apply to Django Ninja**:
```python
# Future implementation (Phase 3)
import hmac
import hashlib

def verify_line_signature(body: bytes, signature: str) -> bool:
    secret = settings.LINE_CHANNEL_SECRET.encode()
    hash_digest = hmac.new(secret, body, hashlib.sha256).digest()
    expected = base64.b64encode(hash_digest).decode()
    return hmac.compare_digest(signature, expected)
```

### A.3 Database Pattern (from LINE_chat_id/database.py)

**SQLAlchemy Pattern**:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///./line_bot.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**Django Equivalent**:
```python
# Django handles this automatically via ORM
# Just use:
from social.models import PostTransaction

# In views:
async def get_post(post_id):
    post = await PostTransaction.objects.aget(pk=post_id)
    return post
```

---

## Appendix B: Migration from FastAPI to Django

### Differences to Note

| Feature | FastAPI (LINE example) | Django + Ninja |
|---------|----------------------|----------------|
| **App Initialization** | `app = FastAPI()` | Django project structure |
| **Database** | SQLAlchemy ORM | Django ORM |
| **Async** | Native async/await | Django 4.1+ async ORM + `sync_to_async` |
| **Validation** | Pydantic models | Pydantic + Django models |
| **Admin** | None (manual) | Django Admin + Wagtail |
| **Tasks** | Manual | Celery |
| **Config** | `.env` + manual | Django settings + `.env` |

### Key Advantages of Django Stack

1. **Built-in Admin**: Django Admin + Wagtail CMS
2. **ORM**: Django ORM is mature and well-tested
3. **Migrations**: Automatic schema versioning
4. **Security**: CSRF, XSS protection built-in
5. **Ecosystem**: Huge library of Django packages
6. **CMS**: Wagtail for content management

---

## Appendix C: Quick Start Guide

For new developers joining the project:

```bash
# 1. Clone repository
git clone <repo-url>
cd CRUDtest

# 2. Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment template
cp .env.example .env
# Edit .env with your credentials

# 5. Run migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Start Redis (in separate terminal)
redis-server

# 8. Start Celery worker (in separate terminal)
celery -A config worker -l info

# 9. Start Django server
python manage.py runserver

# 10. Access the application
# Django Admin: http://localhost:8000/admin
# Wagtail CMS: http://localhost:8000/cms
# API Docs: http://localhost:8000/api/docs

# 11. Run tests
pytest
```

---

**End of PRD - Phase 1**

For questions or clarifications, refer to:
- `INITIAL.md` - Comprehensive project specification
- `CLAUDE.md` - Project guidelines and standards
- Django documentation: https://docs.djangoproject.com/en/5.0/
- Wagtail documentation: https://docs.wagtail.org/
- Django Ninja documentation: https://django-ninja.dev/
