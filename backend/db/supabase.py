"""
Supabase client module.

This module provides functions for interacting with Supabase.
"""

import logging
from functools import lru_cache

from supabase import Client, create_client

from backend.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get a cached Supabase client instance.
    
    Returns:
        A Supabase client instance.
    """
    try:
        # Create and return a Supabase client
        return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    except Exception as e:
        logger.error(f"Failed to create Supabase client: {str(e)}")
        raise 