"""
User model module.

This module defines the User model for authentication.
"""

from pydantic import BaseModel, EmailStr, Field, model_validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID


class User(BaseModel):
    """User model for authentication and user management."""
    
    id: UUID
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "user"  # Can be "admin", "user", or other roles
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @model_validator(mode='before')
    @classmethod
    def validate_string_id(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and convert created_at and updated_at strings to datetime objects."""
        if isinstance(data, dict):
            # Convert created_at from string to datetime if needed
            if isinstance(data.get('created_at'), str):
                data['created_at'] = datetime.fromisoformat(
                    data['created_at'].replace('Z', '+00:00')
                )
                
            # Convert updated_at from string to datetime if needed
            if data.get('updated_at') and isinstance(data.get('updated_at'), str):
                data['updated_at'] = datetime.fromisoformat(
                    data['updated_at'].replace('Z', '+00:00')
                )
                
        return data
    
    class Config:
        from_attributes = True 