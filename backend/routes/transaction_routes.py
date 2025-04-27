"""
Transaction routes.

This module defines the FastAPI routes for transaction operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.models.transaction import Transaction, TransactionCreate, TransactionUpdate
from backend.services.transaction_service import TransactionService

router = APIRouter(prefix="/transactions", tags=["transactions"])


def get_transaction_service() -> TransactionService:
    """
    Get the transaction service instance.
    
    Returns:
        A TransactionService instance.
    """
    return TransactionService()


@router.post("", response_model=Transaction, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    service: TransactionService = Depends(get_transaction_service)
) -> Transaction:
    """
    Create a new transaction.
    
    Args:
        transaction_data: The transaction data.
        service: The transaction service.
        
    Returns:
        The created transaction.
    """
    return await service.create_transaction(transaction_data)


@router.get("", response_model=List[Transaction])
async def list_transactions(
    skip: int = 0,
    limit: int = 100,
    service: TransactionService = Depends(get_transaction_service)
) -> List[Transaction]:
    """
    Get a list of transactions.
    
    Args:
        skip: The number of transactions to skip.
        limit: The maximum number of transactions to return.
        service: The transaction service.
        
    Returns:
        A list of transactions.
    """
    return await service.list_transactions(skip, limit)


@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(
    transaction_id: UUID,
    service: TransactionService = Depends(get_transaction_service)
) -> Transaction:
    """
    Get a transaction by ID.
    
    Args:
        transaction_id: The ID of the transaction to get.
        service: The transaction service.
        
    Returns:
        The transaction if found.
        
    Raises:
        HTTPException: If the transaction is not found.
    """
    transaction = await service.get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found"
        )
    return transaction


@router.put("/{transaction_id}", response_model=Transaction)
async def update_transaction(
    transaction_id: UUID,
    transaction_data: TransactionUpdate,
    service: TransactionService = Depends(get_transaction_service)
) -> Transaction:
    """
    Update a transaction.
    
    Args:
        transaction_id: The ID of the transaction to update.
        transaction_data: The updated transaction data.
        service: The transaction service.
        
    Returns:
        The updated transaction.
        
    Raises:
        HTTPException: If the transaction is not found.
    """
    transaction = await service.update_transaction(transaction_id, transaction_data)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found"
        )
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID,
    service: TransactionService = Depends(get_transaction_service)
) -> None:
    """
    Delete a transaction.
    
    Args:
        transaction_id: The ID of the transaction to delete.
        service: The transaction service.
        
    Raises:
        HTTPException: If the transaction is not found.
    """
    deleted = await service.delete_transaction(transaction_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found"
        )


@router.get("/driver/{driver_id}", response_model=List[Transaction])
async def get_transactions_by_driver(
    driver_id: UUID,
    skip: int = 0,
    limit: int = 100,
    service: TransactionService = Depends(get_transaction_service)
) -> List[Transaction]:
    """
    Get transactions by driver.
    
    Args:
        driver_id: The driver ID to filter by.
        skip: The number of transactions to skip.
        limit: The maximum number of transactions to return.
        service: The transaction service.
        
    Returns:
        A list of transactions for the specified driver.
    """
    return await service.get_transactions_by_driver(driver_id, skip, limit)


@router.get("/vehicle/{vehicle_id}", response_model=List[Transaction])
async def get_transactions_by_vehicle(
    vehicle_id: UUID,
    skip: int = 0,
    limit: int = 100,
    service: TransactionService = Depends(get_transaction_service)
) -> List[Transaction]:
    """
    Get transactions by vehicle.
    
    Args:
        vehicle_id: The vehicle ID to filter by.
        skip: The number of transactions to skip.
        limit: The maximum number of transactions to return.
        service: The transaction service.
        
    Returns:
        A list of transactions for the specified vehicle.
    """
    return await service.get_transactions_by_vehicle(vehicle_id, skip, limit)


@router.get("/date-range", response_model=List[Transaction])
async def get_transactions_by_date_range(
    start_date: datetime = Query(..., description="Start date for filtering transactions"),
    end_date: datetime = Query(..., description="End date for filtering transactions"),
    skip: int = 0,
    limit: int = 100,
    service: TransactionService = Depends(get_transaction_service)
) -> List[Transaction]:
    """
    Get transactions by date range.
    
    Args:
        start_date: The start date to filter by.
        end_date: The end date to filter by.
        skip: The number of transactions to skip.
        limit: The maximum number of transactions to return.
        service: The transaction service.
        
    Returns:
        A list of transactions within the specified date range.
    """
    return await service.get_transactions_by_date_range(start_date, end_date, skip, limit) 