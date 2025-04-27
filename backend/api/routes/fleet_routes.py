"""
Fleet routes for the API.

This module handles endpoints related to fleet management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from backend.api.auth import get_current_user
from backend.models.user import User

# Create router for fleet endpoints
router = APIRouter(prefix="/fleets", tags=["fleets"])


@router.get("/")
async def get_all_fleets(current_user: User = Depends(get_current_user)):
    """
    Get all fleets.
    
    Args:
        current_user: Currently authenticated user from token validation.
        
    Returns:
        List of fleets.
    """
    # This is a stub implementation
    return {"message": "List of fleets will be implemented soon"} 