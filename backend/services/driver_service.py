"""
Driver service.

This module provides services for driver operations.
"""

from typing import List, Optional
from uuid import UUID

from backend.db.supabase import get_supabase_client
from backend.models.driver import Driver, DriverCreate, DriverUpdate


class DriverService:
    """Service for driver operations."""

    async def create_driver(self, driver_data: DriverCreate) -> Driver:
        """
        Create a new driver.
        
        Args:
            driver_data: The driver data.
            
        Returns:
            The created driver.
        """
        supabase = get_supabase_client()
        response = supabase.table("drivers").insert(driver_data.dict()).execute()
        return Driver(**response.data[0])

    async def get_driver(self, driver_id: UUID) -> Optional[Driver]:
        """
        Get a driver by ID.
        
        Args:
            driver_id: The ID of the driver to get.
            
        Returns:
            The driver if found, None otherwise.
        """
        supabase = get_supabase_client()
        response = supabase.table("drivers").select("*").eq("id", str(driver_id)).execute()
        if not response.data:
            return None
        return Driver(**response.data[0])

    async def update_driver(self, driver_id: UUID, driver_data: DriverUpdate) -> Optional[Driver]:
        """
        Update a driver.
        
        Args:
            driver_id: The ID of the driver to update.
            driver_data: The updated driver data.
            
        Returns:
            The updated driver if found, None otherwise.
        """
        supabase = get_supabase_client()
        response = (
            supabase.table("drivers")
            .update(driver_data.dict(exclude_unset=True))
            .eq("id", str(driver_id))
            .execute()
        )
        if not response.data:
            return None
        return Driver(**response.data[0])

    async def delete_driver(self, driver_id: UUID) -> bool:
        """
        Delete a driver.
        
        Args:
            driver_id: The ID of the driver to delete.
            
        Returns:
            True if the driver was deleted, False otherwise.
        """
        supabase = get_supabase_client()
        response = supabase.table("drivers").delete().eq("id", str(driver_id)).execute()
        return bool(response.data)

    async def list_drivers(self, skip: int = 0, limit: int = 100) -> List[Driver]:
        """
        Get a list of drivers.
        
        Args:
            skip: The number of drivers to skip.
            limit: The maximum number of drivers to return.
            
        Returns:
            A list of drivers.
        """
        supabase = get_supabase_client()
        response = (
            supabase.table("drivers")
            .select("*")
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [Driver(**driver) for driver in response.data]

    async def get_drivers_by_status(
        self, status: str, skip: int = 0, limit: int = 100
    ) -> List[Driver]:
        """
        Get drivers by status.
        
        Args:
            status: The status to filter by.
            skip: The number of drivers to skip.
            limit: The maximum number of drivers to return.
            
        Returns:
            A list of drivers with the specified status.
        """
        supabase = get_supabase_client()
        response = (
            supabase.table("drivers")
            .select("*")
            .eq("status", status)
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [Driver(**driver) for driver in response.data]

    async def get_drivers_by_fleet(
        self, fleet_id: str, skip: int = 0, limit: int = 100
    ) -> List[Driver]:
        """
        Get drivers by fleet.
        
        Args:
            fleet_id: The fleet ID to filter by.
            skip: The number of drivers to skip.
            limit: The maximum number of drivers to return.
            
        Returns:
            A list of drivers in the specified fleet.
        """
        supabase = get_supabase_client()
        response = (
            supabase.table("drivers")
            .select("*")
            .eq("fleet_id", fleet_id)
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [Driver(**driver) for driver in response.data] 