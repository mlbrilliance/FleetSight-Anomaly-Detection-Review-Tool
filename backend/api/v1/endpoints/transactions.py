"""
Transactions API endpoints.

This module defines the API endpoints for fleet transactions,
including fuel, maintenance, and other transaction types.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from backend.config import Settings, get_settings
from backend.db.interface import DatabaseInterface
from backend.db.supabase_client import SupabaseClient
from shared_models.models import FleetTransaction

router = APIRouter(
    prefix="/transactions",
    tags=["transactions"],
)


def get_db(settings: Settings = Depends(get_settings)) -> DatabaseInterface:
    """
    Get database client as a dependency.
    
    Args:
        settings: Application settings with database configuration.
        
    Returns:
        DatabaseInterface implementation.
    """
    return SupabaseClient(settings.supabase_url, settings.supabase_key)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_transactions(
    transactions: List[FleetTransaction],
    db: DatabaseInterface = Depends(get_db),
) -> JSONResponse:
    """
    Create multiple transactions.
    
    Args:
        transactions: List of transaction objects.
        db: Database interface.
        
    Returns:
        JSON response with creation status.
        
    Raises:
        HTTPException: If transactions list is empty or on database error.
    """
    if not transactions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No transactions provided",
        )
    
    success, entities = await db.batch_create(transactions)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create transactions",
        )
    
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "status": "success",
            "created": len(entities),
            "message": f"Successfully created {len(entities)} transactions",
        },
    )


@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    db: DatabaseInterface = Depends(get_db),
) -> FleetTransaction:
    """
    Get a transaction by ID.
    
    Args:
        transaction_id: ID of the transaction to retrieve.
        db: Database interface.
        
    Returns:
        Transaction object.
        
    Raises:
        HTTPException: If transaction not found.
    """
    transaction = await db.get_by_id(FleetTransaction, transaction_id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )
    
    return transaction


@router.get("/")
async def get_all_transactions(
    db: DatabaseInterface = Depends(get_db),
) -> List[FleetTransaction]:
    """
    Get all transactions.
    
    Args:
        db: Database interface.
        
    Returns:
        List of transaction objects.
    """
    transactions = await db.get_all(FleetTransaction)
    return transactions


@router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: str,
    transaction: FleetTransaction,
    db: DatabaseInterface = Depends(get_db),
) -> FleetTransaction:
    """
    Update a transaction.
    
    Args:
        transaction_id: ID of the transaction to update.
        transaction: Updated transaction object.
        db: Database interface.
        
    Returns:
        Updated transaction object.
        
    Raises:
        HTTPException: If transaction not found or on database error.
    """
    existing = await db.get_by_id(FleetTransaction, transaction_id)
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )
    
    # Ensure ID matches
    if transaction.id != transaction_id:
        transaction.id = transaction_id
    
    success, updated = await db.update(transaction)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update transaction",
        )
    
    return updated


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    db: DatabaseInterface = Depends(get_db),
) -> None:
    """
    Delete a transaction.
    
    Args:
        transaction_id: ID of the transaction to delete.
        db: Database interface.
        
    Raises:
        HTTPException: If transaction not found or on database error.
    """
    existing = await db.get_by_id(FleetTransaction, transaction_id)
    
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found",
        )
    
    success = await db.delete(FleetTransaction, transaction_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete transaction",
        ) 