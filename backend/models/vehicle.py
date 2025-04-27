"""
Vehicle model.

This module defines the Vehicle model and related schemas.
"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4


class VehicleStatus(str, Enum):
    """Enum for vehicle status."""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    REPAIR = "repair"
    INACTIVE = "inactive"
    RESERVED = "reserved"


class VehicleType(str, Enum):
    """Enum for vehicle types."""
    CAR = "car"
    TRUCK = "truck"
    VAN = "van"
    SUV = "suv"
    MOTORCYCLE = "motorcycle"
    OTHER = "other"


class VehicleBase(BaseModel):
    """Base vehicle model with common attributes."""
    make: str
    model: str
    year: int
    license_plate: str
    vin: str
    status: VehicleStatus = VehicleStatus.ACTIVE
    vehicle_type: VehicleType
    mileage: Optional[int] = None
    fuel_type: Optional[str] = None
    color: Optional[str] = None
    notes: Optional[str] = None


class VehicleCreate(VehicleBase):
    """Schema for creating a new vehicle."""
    pass


class VehicleUpdate(BaseModel):
    """Schema for updating a vehicle."""
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    license_plate: Optional[str] = None
    vin: Optional[str] = None
    status: Optional[VehicleStatus] = None
    vehicle_type: Optional[VehicleType] = None
    mileage: Optional[int] = None
    fuel_type: Optional[str] = None
    color: Optional[str] = None
    notes: Optional[str] = None


class Vehicle(VehicleBase):
    """Complete vehicle model with all attributes."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic model configuration."""
        from_attributes = True 