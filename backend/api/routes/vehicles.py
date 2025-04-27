"""
Vehicle routes.

This module defines API routes for vehicle management.
"""

from fastapi import APIRouter, HTTPException, status, Response
from typing import List, Optional
from uuid import UUID

from backend.models.vehicle import Vehicle, VehicleCreate, VehicleUpdate
from backend.services import fleet_service

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("/", response_model=List[Vehicle])
async def read_vehicles():
    """
    Get all vehicles.
    
    Returns a list of all vehicles in the system.
    """
    return await fleet_service.get_vehicles()


@router.get("/{vehicle_id}", response_model=Vehicle)
async def read_vehicle(vehicle_id: str):
    """
    Get a vehicle by ID.
    
    Args:
        vehicle_id: The ID of the vehicle to retrieve
        
    Returns:
        The vehicle if found
        
    Raises:
        HTTPException: 404 if vehicle not found
    """
    vehicle = await fleet_service.get_vehicle_by_id(vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found"
        )
    return vehicle


@router.post("/", response_model=Vehicle, status_code=status.HTTP_201_CREATED)
async def create_vehicle(vehicle: VehicleCreate):
    """
    Create a new vehicle.
    
    Args:
        vehicle: The vehicle data to create
        
    Returns:
        The created vehicle
    """
    return await fleet_service.create_vehicle(vehicle)


@router.put("/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(vehicle_id: str, vehicle: VehicleUpdate):
    """
    Update an existing vehicle.
    
    Args:
        vehicle_id: The ID of the vehicle to update
        vehicle: The vehicle data to update
        
    Returns:
        The updated vehicle
        
    Raises:
        HTTPException: 404 if vehicle not found
    """
    updated_vehicle = await fleet_service.update_vehicle(vehicle_id, vehicle)
    if not updated_vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found"
        )
    return updated_vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(vehicle_id: str):
    """
    Delete a vehicle.
    
    Args:
        vehicle_id: The ID of the vehicle to delete
        
    Returns:
        No content on success
        
    Raises:
        HTTPException: 404 if vehicle not found
    """
    deleted = await fleet_service.delete_vehicle(vehicle_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT) 