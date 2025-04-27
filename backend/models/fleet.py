"""
Fleet model module.

This module defines the Fleet data model.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class Fleet(BaseModel):
    """Fleet model for storing fleet information."""
    
    id: UUID
    name: str
    description: Optional[str] = None
    location: Optional[str] = None
    manager_id: Optional[UUID] = None
    status: str = "active"
    vehicle_count: int = 0
    driver_count: int = 0
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True