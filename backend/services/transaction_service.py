"""
Transaction service.

This module provides services for transaction operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from backend.db.supabase import get_supabase_client
from backend.models.transaction import Transaction, TransactionCreate, TransactionUpdate


class TransactionService:
    """Service for transaction operations."""

    async def create_transaction(self, transaction_data: TransactionCreate) -> Transaction:
        """
        Create a new transaction.
        
        Args:
            transaction_data: The transaction data.
            
        Returns:
            The created transaction.
        """
        supabase = get_supabase_client()
        response = supabase.table("transactions").insert(transaction_data.dict()).execute()
        return Transaction(**response.data[0])

    async def get_transaction(self, transaction_id: UUID) -> Optional[Transaction]:
        """
        Get a transaction by ID.
        
        Args:
            transaction_id: The ID of the transaction to get.
            
        Returns:
            The transaction if found, None otherwise.
        """
        supabase = get_supabase_client()
        response = supabase.table("transactions").select("*").eq("id", str(transaction_id)).execute()
        if not response.data:
            return None
        return Transaction(**response.data[0])

    async def update_transaction(
        self, transaction_id: UUID, transaction_data: TransactionUpdate
    ) -> Optional[Transaction]:
        """
        Update a transaction.
        
        Args:
            transaction_id: The ID of the transaction to update.
            transaction_data: The updated transaction data.
            
        Returns:
            The updated transaction if found, None otherwise.
        """
        supabase = get_supabase_client()
        response = (
            supabase.table("transactions")
            .update(transaction_data.dict(exclude_unset=True))
            .eq("id", str(transaction_id))
            .execute()
        )
        if not response.data:
            return None
        return Transaction(**response.data[0])

    async def delete_transaction(self, transaction_id: UUID) -> bool:
        """
        Delete a transaction.
        
        Args:
            transaction_id: The ID of the transaction to delete.
            
        Returns:
            True if the transaction was deleted, False otherwise.
        """
        supabase = get_supabase_client()
        response = supabase.table("transactions").delete().eq("id", str(transaction_id)).execute()
        return bool(response.data)

    async def list_transactions(self, skip: int = 0, limit: int = 100) -> List[Transaction]:
        """
        Get a list of transactions.
        
        Args:
            skip: The number of transactions to skip.
            limit: The maximum number of transactions to return.
            
        Returns:
            A list of transactions.
        """
        supabase = get_supabase_client()
        response = (
            supabase.table("transactions")
            .select("*")
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [Transaction(**transaction) for transaction in response.data]

    async def get_transactions_by_vehicle(
        self, vehicle_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        """
        Get transactions by vehicle.
        
        Args:
            vehicle_id: The vehicle ID to filter by.
            skip: The number of transactions to skip.
            limit: The maximum number of transactions to return.
            
        Returns:
            A list of transactions for the specified vehicle.
        """
        supabase = get_supabase_client()
        response = (
            supabase.table("transactions")
            .select("*")
            .eq("vehicle_id", str(vehicle_id))
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [Transaction(**transaction) for transaction in response.data]

    async def get_transactions_by_driver(
        self, driver_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        """
        Get transactions by driver.
        
        Args:
            driver_id: The driver ID to filter by.
            skip: The number of transactions to skip.
            limit: The maximum number of transactions to return.
            
        Returns:
            A list of transactions for the specified driver.
        """
        supabase = get_supabase_client()
        response = (
            supabase.table("transactions")
            .select("*")
            .eq("driver_id", str(driver_id))
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [Transaction(**transaction) for transaction in response.data]

    async def get_transactions_by_date_range(
        self, start_date: datetime, end_date: datetime, skip: int = 0, limit: int = 100
    ) -> List[Transaction]:
        """
        Get transactions by date range.
        
        Args:
            start_date: The start date to filter by.
            end_date: The end date to filter by.
            skip: The number of transactions to skip.
            limit: The maximum number of transactions to return.
            
        Returns:
            A list of transactions within the specified date range.
        """
        supabase = get_supabase_client()
        response = (
            supabase.table("transactions")
            .select("*")
            .gte("transaction_date", start_date.isoformat())
            .lte("transaction_date", end_date.isoformat())
            .range(skip, skip + limit - 1)
            .execute()
        )
        return [Transaction(**transaction) for transaction in response.data] 