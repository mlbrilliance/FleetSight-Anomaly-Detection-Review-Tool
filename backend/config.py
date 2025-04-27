"""
Configuration management for FleetSight application.

This module loads configuration from environment variables, provides
defaults, and validates the configuration following the project's
ontology definitions.

References:
- owl/fleetsight-system.ttl: Contains configuration-related concepts
"""

import os
import secrets
from enum import Enum
from functools import lru_cache
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator


class EnvironmentType(str, Enum):
    """Environment types as defined in owl/fleetsight-system.ttl#Environment"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(str, Enum):
    """Log levels as defined in owl/fleetsight-system.ttl#LogLevel"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Maps to owl/fleetsight-system.ttl#SystemConfiguration
    """
    # Core application settings
    APP_NAME: str = "FleetSight"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: EnvironmentType = EnvironmentType.DEVELOPMENT
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """Validate and process CORS origins"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database configuration
    # For Supabase, we'll need URL, API key, and other parameters
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_SERVICE_KEY: Optional[str] = None
    
    # For direct Postgres access (if needed)
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """Construct database URI from components if not directly provided"""
        if isinstance(v, str):
            return v
        
        # Skip if any required values are missing
        required = {"POSTGRES_SERVER", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"}
        if not all(values.get(k) for k in required):
            return None
            
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # Logging configuration
    LOG_LEVEL: LogLevel = LogLevel.INFO
    LOG_FORMAT: str = "%(levelname)s: %(message)s"
    
    # ML Model configuration 
    MODEL_PATH: Optional[str] = None
    ANOMALY_THRESHOLD: float = 0.8
    
    class Config:
        """Pydantic config"""
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings, with caching to avoid repeated loading.
    
    Returns:
        Settings: The application settings object
    """
    return Settings() 