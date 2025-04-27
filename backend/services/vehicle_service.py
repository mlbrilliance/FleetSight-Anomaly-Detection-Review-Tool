"""
Vehicle service.

This module provides services for vehicle operations.
"""

from typing import List, Optional
from uuid import UUID

from backend.db.supabase import get_supabase_client
from backend.models.vehicle import Vehicle, VehicleCreate, VehicleUpdate


class VehicleService:
    """Service for vehicle operations."""

    async def create_vehicle(self, vehicle_data: VehicleCreate) -> Vehicle:
        """
        Create a new vehicle.
        
        Args:
            vehicle_data: The vehicle data.
            
        Returns:
            The created vehicle.
        """
        supabase = get_supabase_client()
        response = supabase.table("vehicles").insert(vehicle_data.dict()).execute()
        return Vehicle(**response.data[0])

    async def get_vehicle(self, vehicle_id: UUID) -> Optional[Vehicle]:
        """
        Get a vehicle by ID.
        
        Args:
            vehicle_id: The ID of the vehicle to get.
            
        Returns:
            The vehicle if found, None otherwise.
        """
        supabase = get_supabase_client()
        response = supabase.table("vehicles").select("*").eq("id", str(vehicle_id)).execute()
        if not response.data:
            return None
        return Vehicle(**response.data[0])

    async def update_vehicle(self, vehicle_id: UUID, vehicle_data: VehicleUpdate) -> Optional[Vehicle]:
        """
        Update a vehicle.
        
        Args:
            vehicle_id: The ID of the vehicle to update.
            vehicle_data: The updated vehicle data.
            
        Returns:
            The updated vehicle if found, None otherwise.
        """
        supabase = get_supabase_client()
        response = (
            supabase.table("vehicles")
            .update(vehicle_data.dict(exclude_unset=True))
            .eq("id", str(vehicle_id))
            .execute()
        )
        if not response.data:
            return None
        return Vehicle(**response.data[0])

    async def delete_vehicle(self, vehicle_id: UUID) -> bool:
        """
        Delete a vehicle.
        
        Args:
            vehicle_id: The ID of the vehicle to delete.
            
        Returns:
            True if the vehicle was deleted, False otherwise.
        """
        supabase = get_supabase_client()
        response = supabase.table("vehicles").delete().eq("id", str(vehicle_id)).execute()
        return bool(response.data)

    async def list_vehicles(self, skip: int = 0, limit: int = 100) -> List[Vehicle]:
        """
        Get a list of vehicles.
        
        Args:
            skip: The number of vehicles to skip.
            limit: The maximum number of vehicles to return.
            
        Returns:
            A list of vehicles.
        """
        supabase = get_supabase_client()
        response = (
            supabase.table("vehicles")
            .select("*")
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [Vehicle(**vehicle) for vehicle in response.data]

    async def get_vehicles_by_status(
        self, status: str, skip: int = 0, limit: int = 100
    ) -> List[Vehicle]:
        """
        Get vehicles by status.
        
        Args:
            status: The status to filter by.
            skip: The number of vehicles to skip.
            limit: The maximum number of vehicles to return.
            
        Returns:
            A list of vehicles with the specified status.
        """
        supabase = get_supabase_client()
        response = (
            supabase.table("vehicles")
            .select("*")
            .eq("status", status)
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [Vehicle(**vehicle) for vehicle in response.data]

    async def get_vehicles_by_fleet(
        self, fleet_id: str, skip: int = 0, limit: int = 100
    ) -> List[Vehicle]:
        """
        Get vehicles by fleet.
        
        Args:
            fleet_id: The fleet ID to filter by.
            skip: The number of vehicles to skip.
            limit: The maximum number of vehicles to return.
            
        Returns:
            A list of vehicles in the specified fleet.
        """
        supabase = get_supabase_client()
        response = (
            supabase.table("vehicles")
            .select("*")
            .eq("fleet_id", fleet_id)
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [Vehicle(**vehicle) for vehicle in response.data] 