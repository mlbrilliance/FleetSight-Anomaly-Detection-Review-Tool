"""
Vehicle routes.

This module defines the FastAPI routes for vehicle operations.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from backend.models.vehicle import Vehicle, VehicleCreate, VehicleUpdate
from backend.services.vehicle_service import VehicleService

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


def get_vehicle_service() -> VehicleService:
    """
    Get the vehicle service instance.
    
    Returns:
        A VehicleService instance.
    """
    return VehicleService()


@router.post("", response_model=Vehicle, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    service: VehicleService = Depends(get_vehicle_service)
) -> Vehicle:
    """
    Create a new vehicle.
    
    Args:
        vehicle_data: The vehicle data.
        service: The vehicle service.
        
    Returns:
        The created vehicle.
    """
    return await service.create_vehicle(vehicle_data)


@router.get("", response_model=List[Vehicle])
async def list_vehicles(
    skip: int = 0,
    limit: int = 100,
    service: VehicleService = Depends(get_vehicle_service)
) -> List[Vehicle]:
    """
    Get a list of vehicles.
    
    Args:
        skip: The number of vehicles to skip.
        limit: The maximum number of vehicles to return.
        service: The vehicle service.
        
    Returns:
        A list of vehicles.
    """
    return await service.list_vehicles(skip, limit)


@router.get("/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(
    vehicle_id: UUID,
    service: VehicleService = Depends(get_vehicle_service)
) -> Vehicle:
    """
    Get a vehicle by ID.
    
    Args:
        vehicle_id: The ID of the vehicle to get.
        service: The vehicle service.
        
    Returns:
        The vehicle if found.
        
    Raises:
        HTTPException: If the vehicle is not found.
    """
    vehicle = await service.get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found"
        )
    return vehicle


@router.put("/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(
    vehicle_id: UUID,
    vehicle_data: VehicleUpdate,
    service: VehicleService = Depends(get_vehicle_service)
) -> Vehicle:
    """
    Update a vehicle.
    
    Args:
        vehicle_id: The ID of the vehicle to update.
        vehicle_data: The updated vehicle data.
        service: The vehicle service.
        
    Returns:
        The updated vehicle.
        
    Raises:
        HTTPException: If the vehicle is not found.
    """
    vehicle = await service.update_vehicle(vehicle_id, vehicle_data)
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found"
        )
    return vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: UUID,
    service: VehicleService = Depends(get_vehicle_service)
) -> None:
    """
    Delete a vehicle.
    
    Args:
        vehicle_id: The ID of the vehicle to delete.
        service: The vehicle service.
        
    Raises:
        HTTPException: If the vehicle is not found.
    """
    deleted = await service.delete_vehicle(vehicle_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle with ID {vehicle_id} not found"
        )


@router.get("/status/{status}", response_model=List[Vehicle])
async def get_vehicles_by_status(
    status: str,
    skip: int = 0,
    limit: int = 100,
    service: VehicleService = Depends(get_vehicle_service)
) -> List[Vehicle]:
    """
    Get vehicles by status.
    
    Args:
        status: The status to filter by.
        skip: The number of vehicles to skip.
        limit: The maximum number of vehicles to return.
        service: The vehicle service.
        
    Returns:
        A list of vehicles with the specified status.
    """
    return await service.get_vehicles_by_status(status, skip, limit)


@router.get("/fleet/{fleet_id}", response_model=List[Vehicle])
async def get_vehicles_by_fleet(
    fleet_id: str,
    skip: int = 0,
    limit: int = 100,
    service: VehicleService = Depends(get_vehicle_service)
) -> List[Vehicle]:
    """
    Get vehicles by fleet.
    
    Args:
        fleet_id: The fleet ID to filter by.
        skip: The number of vehicles to skip.
        limit: The maximum number of vehicles to return.
        service: The vehicle service.
        
    Returns:
        A list of vehicles in the specified fleet.
    """
    return await service.get_vehicles_by_fleet(fleet_id, skip, limit) 