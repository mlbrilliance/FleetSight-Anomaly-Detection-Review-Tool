"""
Supabase client module.

This module provides a client for interacting with the Supabase database.
"""

import os
from functools import lru_cache
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


@lru_cache()
def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance.
    
    Returns:
        A Supabase client instance
        
    Raises:
        ValueError: If Supabase credentials are not set
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase credentials not set. Please check your environment variables.")
    
    return create_client(SUPABASE_URL, SUPABASE_KEY) 