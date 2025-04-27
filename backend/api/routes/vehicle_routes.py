"""
Vehicle routes for the API.

This module handles endpoints related to vehicle management.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.api.auth import get_current_user
from backend.models.vehicle import Vehicle, VehicleCreate, VehicleUpdate
from backend.models.user import User
from backend.services.vehicle_service import VehicleService

# Create router for vehicle endpoints
router = APIRouter(prefix="/vehicles", tags=["vehicles"])
vehicle_service = VehicleService()


@router.post("/", response_model=Vehicle)
async def create_vehicle(vehicle: VehicleCreate, _=Depends(get_current_user)):
    """
    Create a new vehicle.
    
    Args:
        vehicle: The vehicle data.
        
    Returns:
        The created vehicle.
    """
    return await vehicle_service.create_vehicle(vehicle)


@router.get("/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(vehicle_id: UUID, _=Depends(get_current_user)):
    """
    Get a vehicle by ID.
    
    Args:
        vehicle_id: The ID of the vehicle to get.
        
    Returns:
        The vehicle.
    """
    vehicle = await vehicle_service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.put("/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(
    vehicle_id: UUID, vehicle: VehicleUpdate, _=Depends(get_current_user)
):
    """
    Update a vehicle.
    
    Args:
        vehicle_id: The ID of the vehicle to update.
        vehicle: The updated vehicle data.
        
    Returns:
        The updated vehicle.
    """
    updated_vehicle = await vehicle_service.update_vehicle(vehicle_id, vehicle)
    if not updated_vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return updated_vehicle


@router.delete("/{vehicle_id}", response_model=bool)
async def delete_vehicle(vehicle_id: UUID, _=Depends(get_current_user)):
    """
    Delete a vehicle.
    
    Args:
        vehicle_id: The ID of the vehicle to delete.
        
    Returns:
        True if the vehicle was deleted.
    """
    success = await vehicle_service.delete_vehicle(vehicle_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return success


@router.get("/", response_model=List[Vehicle])
async def list_vehicles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    _=Depends(get_current_user),
):
    """
    Get a list of all vehicles.
    
    Args:
        skip: The number of vehicles to skip.
        limit: The maximum number of vehicles to return.
        
    Returns:
        A list of vehicles.
    """
    return await vehicle_service.list_vehicles(skip=skip, limit=limit)


@router.get("/status/{status}", response_model=List[Vehicle])
async def get_vehicles_by_status(
    status: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    _=Depends(get_current_user),
):
    """
    Get vehicles by status.
    
    Args:
        status: The status to filter by.
        skip: The number of vehicles to skip.
        limit: The maximum number of vehicles to return.
        
    Returns:
        A list of vehicles with the specified status.
    """
    return await vehicle_service.get_vehicles_by_status(
        status=status, skip=skip, limit=limit
    )


@router.get("/fleet/{fleet_id}", response_model=List[Vehicle])
async def get_vehicles_by_fleet(
    fleet_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    _=Depends(get_current_user),
):
    """
    Get vehicles by fleet.
    
    Args:
        fleet_id: The fleet ID to filter by.
        skip: The number of vehicles to skip.
        limit: The maximum number of vehicles to return.
        
    Returns:
        A list of vehicles in the specified fleet.
    """
    return await vehicle_service.get_vehicles_by_fleet(
        fleet_id=str(fleet_id), skip=skip, limit=limit
    )


@router.get("/maintenance-due", response_model=List[Vehicle])
async def get_vehicles_due_for_maintenance(
    days_threshold: int = Query(30, ge=0),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    _=Depends(get_current_user),
):
    """
    Get vehicles due for maintenance.
    
    Args:
        days_threshold: The number of days to look ahead for maintenance due.
        skip: The number of vehicles to skip.
        limit: The maximum number of vehicles to return.
        
    Returns:
        A list of vehicles due for maintenance.
    """
    return await vehicle_service.get_vehicles_due_for_maintenance(
        days_threshold=days_threshold, skip=skip, limit=limit
    )


@router.get("/")
async def get_all_vehicles(current_user: User = Depends(get_current_user)):
    """
    Get all vehicles.
    
    Args:
        current_user: Currently authenticated user from token validation.
        
    Returns:
        List of vehicles.
    """
    # This is a stub implementation
    return {"message": "List of vehicles will be implemented soon"} 