"""
Tests for API health check endpoint.
"""
import pytest
from django.test import AsyncClient


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Test that the health check endpoint returns correct status."""
    client = AsyncClient()
    response = await client.get('/api/health')

    assert response.status_code == 200

    data = response.json()
    assert data['status'] == 'healthy'
    assert data['version'] == '1.0.0'
    assert 'message' in data


@pytest.mark.django_db
@pytest.mark.asyncio
async def test_health_check_structure():
    """Test that the health check response has the expected structure."""
    client = AsyncClient()
    response = await client.get('/api/health')

    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == 3  # status, version, message
    assert all(isinstance(v, str) for v in data.values())
