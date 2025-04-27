"""
Pytest configuration and shared fixtures for backend tests.
[OWL: fleetsight-core-entities.ttl]

This module contains common fixtures and utilities used across test modules.
"""

import os
import sys
import pytest
from datetime import datetime
from uuid import uuid4
from typing import Any, Dict, Optional, List

# Add the project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


@pytest.fixture
def mock_uuid():
    """Return a consistent UUID for testing."""
    return uuid4()


@pytest.fixture
def mock_datetime():
    """Return a consistent datetime for testing."""
    return datetime(2023, 5, 15, 10, 0, 0)


class MockResponse:
    """Mock HTTP response for testing."""
    
    def __init__(self, json_data: Any, status_code: int = 200, headers: Optional[Dict[str, str]] = None):
        self.json_data = json_data
        self.status_code = status_code
        self.headers = headers or {}
        self.text = str(json_data)
    
    def json(self):
        """Return JSON data."""
        return self.json_data
    
    def raise_for_status(self):
        """Raise an exception if status code is 4xx or 5xx."""
        if 400 <= self.status_code < 600:
            from httpx import HTTPStatusError
            raise HTTPStatusError(f"HTTP Error: {self.status_code}", request=None, response=self) 