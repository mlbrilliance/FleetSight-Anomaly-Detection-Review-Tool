"""
Tests for the configuration management system.
"""

import os
from unittest import mock

import pytest

from backend.config import EnvironmentType, LogLevel, Settings, get_settings


def test_default_settings():
    """Test that default settings are correctly initialized."""
    settings = Settings()
    assert settings.APP_NAME == "FleetSight"
    assert settings.API_V1_STR == "/api/v1"
    assert settings.ENVIRONMENT == EnvironmentType.DEVELOPMENT
    assert settings.LOG_LEVEL == LogLevel.INFO
    assert settings.ANOMALY_THRESHOLD == 0.8


def test_environment_enum():
    """Test that EnvironmentType enum contains expected values."""
    assert EnvironmentType.DEVELOPMENT == "development"
    assert EnvironmentType.STAGING == "staging"
    assert EnvironmentType.PRODUCTION == "production"
    assert EnvironmentType.TESTING == "testing"


def test_log_level_enum():
    """Test that LogLevel enum contains expected values."""
    assert LogLevel.DEBUG == "DEBUG"
    assert LogLevel.INFO == "INFO"
    assert LogLevel.WARNING == "WARNING"
    assert LogLevel.ERROR == "ERROR"
    assert LogLevel.CRITICAL == "CRITICAL"


def test_settings_from_env():
    """Test that settings are loaded from environment variables."""
    with mock.patch.dict(
        os.environ,
        {
            "APP_NAME": "TestApp",
            "ENVIRONMENT": "production",
            "LOG_LEVEL": "ERROR",
            "ANOMALY_THRESHOLD": "0.95",
            "BACKEND_CORS_ORIGINS": "http://localhost:3000,http://localhost:8080",
        },
    ):
        settings = Settings()
        assert settings.APP_NAME == "TestApp"
        assert settings.ENVIRONMENT == EnvironmentType.PRODUCTION
        assert settings.LOG_LEVEL == LogLevel.ERROR
        assert settings.ANOMALY_THRESHOLD == 0.95
        assert len(settings.BACKEND_CORS_ORIGINS) == 2
        assert str(settings.BACKEND_CORS_ORIGINS[0]) == "http://localhost:3000"
        assert str(settings.BACKEND_CORS_ORIGINS[1]) == "http://localhost:8080"


def test_assemble_db_connection():
    """Test database URI assembly from components."""
    with mock.patch.dict(
        os.environ,
        {
            "POSTGRES_SERVER": "localhost",
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "password",
            "POSTGRES_DB": "fleetsight",
        },
    ):
        settings = Settings()
        assert settings.SQLALCHEMY_DATABASE_URI is not None
        assert "postgresql://postgres:password@localhost/fleetsight" in str(
            settings.SQLALCHEMY_DATABASE_URI
        )


def test_get_settings_cache():
    """Test that get_settings caches results."""
    first = get_settings()
    second = get_settings()
    assert first is second  # Should be the same instance due to caching 