"""
Driver routes.

This module defines the FastAPI routes for driver operations.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from backend.models.driver import Driver, DriverCreate, DriverUpdate
from backend.services.driver_service import DriverService

router = APIRouter(prefix="/drivers", tags=["drivers"])


def get_driver_service() -> DriverService:
    """
    Get the driver service instance.
    
    Returns:
        A DriverService instance.
    """
    return DriverService()


@router.post("", response_model=Driver, status_code=status.HTTP_201_CREATED)
async def create_driver(
    driver_data: DriverCreate,
    service: DriverService = Depends(get_driver_service)
) -> Driver:
    """
    Create a new driver.
    
    Args:
        driver_data: The driver data.
        service: The driver service.
        
    Returns:
        The created driver.
    """
    return await service.create_driver(driver_data)


@router.get("", response_model=List[Driver])
async def list_drivers(
    skip: int = 0,
    limit: int = 100,
    service: DriverService = Depends(get_driver_service)
) -> List[Driver]:
    """
    Get a list of drivers.
    
    Args:
        skip: The number of drivers to skip.
        limit: The maximum number of drivers to return.
        service: The driver service.
        
    Returns:
        A list of drivers.
    """
    return await service.list_drivers(skip, limit)


@router.get("/{driver_id}", response_model=Driver)
async def get_driver(
    driver_id: UUID,
    service: DriverService = Depends(get_driver_service)
) -> Driver:
    """
    Get a driver by ID.
    
    Args:
        driver_id: The ID of the driver to get.
        service: The driver service.
        
    Returns:
        The driver if found.
        
    Raises:
        HTTPException: If the driver is not found.
    """
    driver = await service.get_driver(driver_id)
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Driver with ID {driver_id} not found"
        )
    return driver


@router.put("/{driver_id}", response_model=Driver)
async def update_driver(
    driver_id: UUID,
    driver_data: DriverUpdate,
    service: DriverService = Depends(get_driver_service)
) -> Driver:
    """
    Update a driver.
    
    Args:
        driver_id: The ID of the driver to update.
        driver_data: The updated driver data.
        service: The driver service.
        
    Returns:
        The updated driver.
        
    Raises:
        HTTPException: If the driver is not found.
    """
    driver = await service.update_driver(driver_id, driver_data)
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Driver with ID {driver_id} not found"
        )
    return driver


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_driver(
    driver_id: UUID,
    service: DriverService = Depends(get_driver_service)
) -> None:
    """
    Delete a driver.
    
    Args:
        driver_id: The ID of the driver to delete.
        service: The driver service.
        
    Raises:
        HTTPException: If the driver is not found.
    """
    deleted = await service.delete_driver(driver_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Driver with ID {driver_id} not found"
        )


@router.get("/status/{status}", response_model=List[Driver])
async def get_drivers_by_status(
    status: str,
    skip: int = 0,
    limit: int = 100,
    service: DriverService = Depends(get_driver_service)
) -> List[Driver]:
    """
    Get drivers by status.
    
    Args:
        status: The status to filter by.
        skip: The number of drivers to skip.
        limit: The maximum number of drivers to return.
        service: The driver service.
        
    Returns:
        A list of drivers with the specified status.
    """
    return await service.get_drivers_by_status(status, skip, limit)


@router.get("/fleet/{fleet_id}", response_model=List[Driver])
async def get_drivers_by_fleet(
    fleet_id: str,
    skip: int = 0,
    limit: int = 100,
    service: DriverService = Depends(get_driver_service)
) -> List[Driver]:
    """
    Get drivers by fleet.
    
    Args:
        fleet_id: The fleet ID to filter by.
        skip: The number of drivers to skip.
        limit: The maximum number of drivers to return.
        service: The driver service.
        
    Returns:
        A list of drivers in the specified fleet.
    """
    return await service.get_drivers_by_fleet(fleet_id, skip, limit) 