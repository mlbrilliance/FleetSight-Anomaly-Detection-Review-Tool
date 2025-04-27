"""
Vehicle repository implementation.

This module implements the repository interface for the Vehicle entity.
"""

from typing import List, Optional
from uuid import UUID

from backend.models.vehicle import Vehicle
from backend.repositories.supabase_repository import SupabaseRepository


class VehicleRepository(SupabaseRepository[Vehicle]):
    """
    Vehicle repository implementation.
    
    Implements the repository interface for the Vehicle entity.
    """
    
    def __init__(self):
        """Initialize the repository with the Vehicle model and table name."""
        super().__init__(Vehicle, "vehicles")
    
    async def find_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[Vehicle]:
        """
        Find vehicles by status.
        
        Args:
            status: The status to filter by.
            skip: The number of items to skip.
            limit: The maximum number of items to return.
            
        Returns:
            A list of vehicles with the specified status.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{self.table_name}",
                params={"status": f"eq.{status}"},
                headers={
                    **self.headers,
                    "Range": f"{skip}-{skip + limit - 1}"
                }
            )
            response.raise_for_status()
            return [Vehicle(**item) for item in response.json()]
    
    async def find_by_fleet(self, fleet_id: str, skip: int = 0, limit: int = 100) -> List[Vehicle]:
        """
        Find vehicles by fleet.
        
        Args:
            fleet_id: The fleet ID to filter by.
            skip: The number of items to skip.
            limit: The maximum number of items to return.
            
        Returns:
            A list of vehicles in the specified fleet.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{self.table_name}",
                params={"fleet_id": f"eq.{fleet_id}"},
                headers={
                    **self.headers,
                    "Range": f"{skip}-{skip + limit - 1}"
                }
            )
            response.raise_for_status()
            return [Vehicle(**item) for item in response.json()] 