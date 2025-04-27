"""
Driver routes for the API.

This module handles endpoints related to driver management.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.api.auth import get_current_user
from backend.models.driver import Driver, DriverCreate, DriverUpdate
from backend.services.driver_service import DriverService
from backend.models.user import User

router = APIRouter(prefix="/drivers", tags=["drivers"])
driver_service = DriverService()


@router.post("/", response_model=Driver)
async def create_driver(driver: DriverCreate, _=Depends(get_current_user)):
    """
    Create a new driver.
    
    Args:
        driver: The driver data.
        
    Returns:
        The created driver.
    """
    return await driver_service.create_driver(driver)


@router.get("/{driver_id}", response_model=Driver)
async def get_driver(driver_id: UUID, _=Depends(get_current_user)):
    """
    Get a driver by ID.
    
    Args:
        driver_id: The ID of the driver to get.
        
    Returns:
        The driver.
    """
    driver = await driver_service.get_driver(driver_id)
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.put("/{driver_id}", response_model=Driver)
async def update_driver(
    driver_id: UUID, driver: DriverUpdate, _=Depends(get_current_user)
):
    """
    Update a driver.
    
    Args:
        driver_id: The ID of the driver to update.
        driver: The updated driver data.
        
    Returns:
        The updated driver.
    """
    updated_driver = await driver_service.update_driver(driver_id, driver)
    if not updated_driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return updated_driver


@router.delete("/{driver_id}", response_model=bool)
async def delete_driver(driver_id: UUID, _=Depends(get_current_user)):
    """
    Delete a driver.
    
    Args:
        driver_id: The ID of the driver to delete.
        
    Returns:
        True if the driver was deleted.
    """
    success = await driver_service.delete_driver(driver_id)
    if not success:
        raise HTTPException(status_code=404, detail="Driver not found")
    return success


@router.get("/", response_model=List[Driver])
async def list_drivers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    _=Depends(get_current_user),
):
    """
    Get a list of all drivers.
    
    Args:
        skip: The number of drivers to skip.
        limit: The maximum number of drivers to return.
        
    Returns:
        A list of drivers.
    """
    return await driver_service.list_drivers(skip=skip, limit=limit)


@router.get("/status/{status}", response_model=List[Driver])
async def get_drivers_by_status(
    status: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    _=Depends(get_current_user),
):
    """
    Get drivers by status.
    
    Args:
        status: The status to filter by.
        skip: The number of drivers to skip.
        limit: The maximum number of drivers to return.
        
    Returns:
        A list of drivers with the specified status.
    """
    return await driver_service.get_drivers_by_status(
        status=status, skip=skip, limit=limit
    )


@router.get("/fleet/{fleet_id}", response_model=List[Driver])
async def get_drivers_by_fleet(
    fleet_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    _=Depends(get_current_user),
):
    """
    Get drivers by fleet.
    
    Args:
        fleet_id: The fleet ID to filter by.
        skip: The number of drivers to skip.
        limit: The maximum number of drivers to return.
        
    Returns:
        A list of drivers in the specified fleet.
    """
    return await driver_service.get_drivers_by_fleet(
        fleet_id=fleet_id, skip=skip, limit=limit
    )


@router.get("/")
async def get_all_drivers(current_user: User = Depends(get_current_user)):
    """
    Get all drivers.
    
    Args:
        current_user: Currently authenticated user from token validation.
        
    Returns:
        List of drivers.
    """
    # This is a stub implementation
    return {"message": "List of drivers will be implemented soon"} 