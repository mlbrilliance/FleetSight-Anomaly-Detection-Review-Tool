"""
Transaction routes for the API.

This module handles endpoints related to financial transactions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from backend.api.auth import get_current_user
from backend.models.user import User

# Create router for transaction endpoints
router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.get("/")
async def get_all_transactions(current_user: User = Depends(get_current_user)):
    """
    Get all transactions.
    
    Args:
        current_user: Currently authenticated user from token validation.
        
    Returns:
        List of transactions.
    """
    # This is a stub implementation
    return {"message": "List of transactions will be implemented soon"} 