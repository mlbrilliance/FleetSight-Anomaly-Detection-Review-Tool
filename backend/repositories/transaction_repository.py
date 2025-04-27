"""
Transaction repository implementation.

This module implements the repository interface for the Transaction entity.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

import httpx

from backend.models.transaction import Transaction
from backend.repositories.supabase_repository import SupabaseRepository


class TransactionRepository(SupabaseRepository[Transaction]):
    """
    Transaction repository implementation.
    
    Implements the repository interface for the Transaction entity.
    """
    
    def __init__(self):
        """Initialize the repository with the Transaction model and table name."""
        super().__init__(Transaction, "transactions")
    
    async def find_by_driver(self, driver_id: UUID, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """
        Find transactions by driver.
        
        Args:
            driver_id: The driver ID to filter by.
            skip: The number of items to skip.
            limit: The maximum number of items to return.
            
        Returns:
            A list of transactions for the specified driver.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{self.table_name}",
                params={"driver_id": f"eq.{driver_id}"},
                headers={
                    **self.headers,
                    "Range": f"{skip}-{skip + limit - 1}"
                }
            )
            response.raise_for_status()
            return [Transaction(**item) for item in response.json()]
    
    async def find_by_vehicle(self, vehicle_id: UUID, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """
        Find transactions by vehicle.
        
        Args:
            vehicle_id: The vehicle ID to filter by.
            skip: The number of items to skip.
            limit: The maximum number of items to return.
            
        Returns:
            A list of transactions for the specified vehicle.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{self.table_name}",
                params={"vehicle_id": f"eq.{vehicle_id}"},
                headers={
                    **self.headers,
                    "Range": f"{skip}-{skip + limit - 1}"
                }
            )
            response.raise_for_status()
            return [Transaction(**item) for item in response.json()]
    
    async def find_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Transaction]:
        """
        Find transactions by date range.
        
        Args:
            start_date: The start date to filter by.
            end_date: The end date to filter by.
            skip: The number of items to skip.
            limit: The maximum number of items to return.
            
        Returns:
            A list of transactions within the specified date range.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{self.table_name}",
                params={
                    "timestamp": f"gte.{start_date.isoformat()}",
                    "timestamp": f"lte.{end_date.isoformat()}"
                },
                headers={
                    **self.headers,
                    "Range": f"{skip}-{skip + limit - 1}"
                }
            )
            response.raise_for_status()
            return [Transaction(**item) for item in response.json()] 