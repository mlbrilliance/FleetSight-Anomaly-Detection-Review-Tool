"""
Transaction model module.

This module defines the Transaction data model.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class Transaction(BaseModel):
    """Transaction model for storing financial transactions."""
    
    id: UUID
    fleet_id: Optional[UUID] = None
    vehicle_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    transaction_type: str
    amount: float
    date: datetime
    location: Optional[str] = None
    odometer_reading: Optional[int] = None
    fuel_amount: Optional[float] = None
    fuel_type: Optional[str] = None
    fuel_price_per_unit: Optional[float] = None
    payment_method: Optional[str] = None
    reference_number: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True 