"""
Pytest configuration and shared fixtures.
"""
import pytest


@pytest.fixture
def api_client():
    """Provide Django test client for API testing."""
    from django.test import Client
    return Client()


@pytest.fixture
async def async_api_client():
    """Provide async test client for API testing."""
    from django.test import AsyncClient
    return AsyncClient()
