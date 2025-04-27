"""
Tests for main.py module.

This module contains tests for the main application endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from backend.main import app


def test_root_endpoint(test_app):
    """Test the root endpoint returns the correct message."""
    response = test_app.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "FleetSight API is running"}


def test_health_check(test_app):
    """Test the health check endpoint returns healthy status."""
    response = test_app.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == "healthy" 