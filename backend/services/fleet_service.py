"""
Fleet service.

This module provides services for managing fleet vehicles.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from backend.models.vehicle import Vehicle, VehicleCreate, VehicleUpdate

# In-memory storage for development/testing
vehicles_db = {}


async def get_vehicles() -> List[Vehicle]:
    """
    Get all vehicles.
    
    Returns:
        List[Vehicle]: List of all vehicles
    """
    return list(vehicles_db.values())


async def get_vehicle_by_id(vehicle_id: str) -> Optional[Vehicle]:
    """
    Get a vehicle by ID.
    
    Args:
        vehicle_id (str): ID of the vehicle to retrieve
        
    Returns:
        Optional[Vehicle]: The vehicle if found, None otherwise
    """
    return vehicles_db.get(vehicle_id)


async def create_vehicle(vehicle_data: VehicleCreate) -> Vehicle:
    """
    Create a new vehicle.
    
    Args:
        vehicle_data (VehicleCreate): Data for the new vehicle
        
    Returns:
        Vehicle: The created vehicle
    """
    now = datetime.now()
    vehicle_id = str(uuid4())
    
    vehicle = Vehicle(
        id=vehicle_id,
        created_at=now,
        updated_at=now,
        **vehicle_data.dict()
    )
    
    vehicles_db[vehicle_id] = vehicle
    return vehicle


async def update_vehicle(vehicle_id: str, vehicle_data: VehicleUpdate) -> Optional[Vehicle]:
    """
    Update an existing vehicle.
    
    Args:
        vehicle_id (str): ID of the vehicle to update
        vehicle_data (VehicleUpdate): New data for the vehicle
        
    Returns:
        Optional[Vehicle]: The updated vehicle if found, None otherwise
    """
    existing_vehicle = await get_vehicle_by_id(vehicle_id)
    
    if not existing_vehicle:
        return None
    
    # Update fields
    update_dict = vehicle_data.dict(exclude_unset=True)
    
    for field, value in update_dict.items():
        setattr(existing_vehicle, field, value)
    
    # Update the updated_at timestamp
    existing_vehicle.updated_at = datetime.now()
    
    # Save back to our "database"
    vehicles_db[vehicle_id] = existing_vehicle
    
    return existing_vehicle


async def delete_vehicle(vehicle_id: str) -> bool:
    """
    Delete a vehicle.
    
    Args:
        vehicle_id (str): ID of the vehicle to delete
        
    Returns:
        bool: True if the vehicle was deleted, False otherwise
    """
    if vehicle_id in vehicles_db:
        del vehicles_db[vehicle_id]
        return True
    return False 