"""
Database package initialization.

This module provides database client and utilities.
"""

from backend.db.supabase_client import get_supabase_client

__all__ = ["get_supabase_client"] 