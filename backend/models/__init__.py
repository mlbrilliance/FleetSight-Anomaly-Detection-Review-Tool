"""
Models package initialization.

This file marks the directory as a Python package.

This module imports all model classes.
"""

from backend.models.user import User
from backend.models.driver import Driver, DriverCreate, DriverUpdate
from backend.models.vehicle import Vehicle, VehicleCreate, VehicleUpdate
from backend.models.fleet import Fleet
from backend.models.transaction import Transaction

__all__ = [
    "User",
    "Driver", "DriverCreate", "DriverUpdate",
    "Vehicle", "VehicleCreate", "VehicleUpdate",
    "Fleet",
    "Transaction",
] 