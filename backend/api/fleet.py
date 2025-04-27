"""
Fleet management API routes.

This module defines the API routes for fleet management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from backend.models.vehicle import Vehicle, VehicleCreate, VehicleUpdate
from backend.models.user import User
from backend.api.auth import get_current_user
from backend.services.fleet_service import (
    get_vehicles, 
    get_vehicle_by_id,
    create_vehicle,
    update_vehicle,
    delete_vehicle
)

router = APIRouter(prefix="/fleet", tags=["fleet"])


@router.get("/vehicles", response_model=List[Vehicle])
async def list_vehicles(
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a list of vehicles in the fleet.
    
    Args:
        status: Optional filter by vehicle status
        limit: Maximum number of vehicles to return
        offset: Number of vehicles to skip for pagination
        current_user: The authenticated user
        
    Returns:
        List of vehicles
    """
    return await get_vehicles(status=status, limit=limit, offset=offset)


@router.get("/vehicles/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(
    vehicle_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a specific vehicle by ID.
    
    Args:
        vehicle_id: The ID of the vehicle to retrieve
        current_user: The authenticated user
        
    Returns:
        The vehicle details
        
    Raises:
        HTTPException: If the vehicle is not found
    """
    vehicle = await get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    return vehicle


@router.post("/vehicles", response_model=Vehicle, status_code=status.HTTP_201_CREATED)
async def add_vehicle(
    vehicle: VehicleCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Add a new vehicle to the fleet.
    
    Args:
        vehicle: The vehicle data to create
        current_user: The authenticated user
        
    Returns:
        The created vehicle details
    """
    return await create_vehicle(vehicle)


@router.put("/vehicles/{vehicle_id}", response_model=Vehicle)
async def modify_vehicle(
    vehicle_id: str,
    vehicle_update: VehicleUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing vehicle.
    
    Args:
        vehicle_id: The ID of the vehicle to update
        vehicle_update: The updated vehicle data
        current_user: The authenticated user
        
    Returns:
        The updated vehicle details
        
    Raises:
        HTTPException: If the vehicle is not found
    """
    updated_vehicle = await update_vehicle(vehicle_id, vehicle_update)
    if not updated_vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    return updated_vehicle


@router.delete("/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_vehicle(
    vehicle_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Remove a vehicle from the fleet.
    
    Args:
        vehicle_id: The ID of the vehicle to delete
        current_user: The authenticated user
        
    Raises:
        HTTPException: If the vehicle is not found
    """
    success = await delete_vehicle(vehicle_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    return None 