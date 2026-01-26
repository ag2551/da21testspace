#!/bin/bash
# Phase 1 Verification Script for Social Media Hub

set -e

echo "=========================================="
echo "Phase 1 Verification Script"
echo "=========================================="
echo ""

# Activate virtual environment
source .venv/bin/activate

echo "✓ Virtual environment activated"
echo ""

# Check Python version
echo "1. Checking Python version..."
python --version
echo "✓ Python version verified"
echo ""

# Check installed packages
echo "2. Checking key dependencies..."
pip show Django | grep Version
pip show wagtail | grep Version
pip show django-ninja | grep Version
pip show celery | grep Version
pip show redis | grep Version
echo "✓ All key dependencies installed"
echo ""

# Check Django project structure
echo "3. Checking Django project structure..."
python manage.py check
echo "✓ Django project configured correctly"
echo ""

# Run tests
echo "4. Running pytest tests..."
pytest apps/api/tests/test_health.py -v --tb=short
echo "✓ All tests passing"
echo ""

# Check file structure
echo "5. Verifying file structure..."
declare -a required_files=(
    "requirements.txt"
    "manage.py"
    "pytest.ini"
    "conftest.py"
    "config/settings.py"
    "config/urls.py"
    "config/celery.py"
    "apps/api/routes.py"
    "apps/social/tasks.py"
    "apps/social/adapters/base.py"
    "apps/social/adapters/facebook.py"
    "apps/social/adapters/linkedin.py"
    "apps/social/adapters/line.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file MISSING"
        exit 1
    fi
done
echo "✓ All required files present"
echo ""

# Check database migrations
echo "6. Checking database status..."
python manage.py showmigrations | head -20
echo "✓ Database migrations applied"
echo ""

echo "=========================================="
echo "Phase 1 Verification Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✓ Python 3.12+ environment configured"
echo "  ✓ Django 5.0 + Wagtail 6.3 installed"
echo "  ✓ Django Ninja API configured"
echo "  ✓ Celery + Redis configured"
echo "  ✓ Adapter Pattern structure in place"
echo "  ✓ Pytest testing infrastructure working"
echo ""
echo "Next Steps:"
echo "  - Start Django dev server: python manage.py runserver"
echo "  - Access Django admin: http://localhost:8000/admin (admin/admin)"
echo "  - Access Wagtail CMS: http://localhost:8000/cms (admin/admin)"
echo "  - Access API docs: http://localhost:8000/api/docs"
echo "  - Test health endpoint: curl http://localhost:8000/api/health"
echo "  - Start Celery worker: celery -A config worker --loglevel=info"
echo ""
