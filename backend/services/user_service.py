"""
User service module.

This module handles user-related operations and authentication.
"""

from typing import Optional
import logging
from uuid import UUID

from backend.db.supabase_client import get_supabase_client
from backend.models.user import User


logger = logging.getLogger(__name__)


async def get_user_by_email(email: str) -> Optional[User]:
    """
    Get a user by email.
    
    Args:
        email: User's email address.
        
    Returns:
        User: User object if found, None otherwise.
    """
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("users").select("*").eq("email", email).execute()
        
        if len(response.data) == 0:
            return None
            
        user_data = response.data[0]
        return User(**user_data)
        
    except Exception as e:
        logger.error(f"Error getting user by email: {e}")
        return None


async def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password.
    
    This function uses Supabase Auth to authenticate the user.
    
    Args:
        email: User's email.
        password: User's password.
        
    Returns:
        User: Authenticated user if successful, None otherwise.
    """
    supabase = get_supabase_client()
    
    try:
        # Use Supabase auth to sign in
        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        # If successful, get the user details
        if auth_response.user:
            # Get user profile data from the users table
            user = await get_user_by_email(email)
            return user
            
        return None
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return None 