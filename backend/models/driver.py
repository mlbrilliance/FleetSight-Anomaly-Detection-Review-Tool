"""
Driver model module.

This module defines the Driver data model.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class Driver(BaseModel):
    """Driver model for storing driver information."""
    
    id: UUID
    fleet_id: Optional[UUID] = None
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    license_number: str
    license_expiry: Optional[datetime] = None
    date_of_birth: Optional[datetime] = None
    date_hired: Optional[datetime] = None
    status: str = "active"
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    next_review_date: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DriverCreate(BaseModel):
    """Driver creation model."""
    
    fleet_id: Optional[UUID] = None
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    license_number: str
    license_expiry: Optional[datetime] = None
    date_of_birth: Optional[datetime] = None
    date_hired: Optional[datetime] = None
    status: str = "active"
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    next_review_date: Optional[datetime] = None
    notes: Optional[str] = None


class DriverUpdate(BaseModel):
    """Driver update model."""
    
    fleet_id: Optional[UUID] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None
    license_expiry: Optional[datetime] = None
    date_of_birth: Optional[datetime] = None
    date_hired: Optional[datetime] = None
    status: Optional[str] = None
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    next_review_date: Optional[datetime] = None
    notes: Optional[str] = None 