"""
Test configuration and fixtures.

This module provides fixtures and configuration for tests.
"""

import asyncio
import pytest
from typing import AsyncGenerator, Dict, Generator
from unittest.mock import patch, MagicMock, AsyncMock
import os
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.main import app
from backend.models.user import User

# Set mock environment variables for testing
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock-key"
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only"


@pytest.fixture
def test_app():
    """Create a test application with mocked dependencies."""
    # Mock Supabase client
    mock_supabase = MagicMock()
    
    # Configure the mock to return appropriate responses
    mock_table = MagicMock()
    mock_table.select.return_value = mock_table
    mock_table.eq.return_value = mock_table
    mock_table.execute.return_value = MagicMock(data=[])
    
    mock_supabase.table.return_value = mock_table
    
    # Mock auth
    mock_supabase.auth = MagicMock()
    
    # Create a valid UUID string
    test_uuid = str(uuid4())
    
    with patch("backend.db.supabase_client.get_supabase_client", return_value=mock_supabase):
        with patch("backend.api.auth.get_current_user", return_value=User(
            id=test_uuid,
            email="test@example.com",
            full_name="Test User",
            role="admin",
            is_active=True,
            created_at="2023-01-01T00:00:00Z"
        )):
            client = TestClient(app)
            yield client 