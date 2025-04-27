"""
Mock settings for testing.

This module provides mock settings for testing purposes.
"""

from typing import List


class MockSettings:
    """Mock application settings for testing."""
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "FleetSight API Test"
    
    # CORS Configuration
    ALLOW_ORIGINS: List[str] = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: List[str] = ["*"]
    ALLOW_HEADERS: List[str] = ["*"]
    
    # Environment
    ENVIRONMENT: str = "test"
    DEBUG: bool = True
    
    # Supabase
    SUPABASE_URL: str = "https://example.supabase.co"
    SUPABASE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock-key"
    
    # JWT settings
    SECRET_KEY: str = "secret_test_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


# Create settings instance
mock_settings = MockSettings() 