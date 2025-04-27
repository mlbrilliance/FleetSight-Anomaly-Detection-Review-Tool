"""
Transaction routes for the API.
[OWL: fleetsight-core-entities.ttl, fleetsight-anomaly.ttl]

This module handles endpoints related to financial transactions,
including transaction creation, retrieval, preprocessing for anomaly detection,
and transaction management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from backend.api.auth import get_current_user
from backend.models.user import User
from backend.models.transaction import Transaction
from backend.repositories.transaction_repository import TransactionRepository
from backend.processing.cleaner import preprocess_data, ProcessedTransaction

# Create router for transaction endpoints
router = APIRouter(prefix="/transactions", tags=["transactions"])

transaction_repo = TransactionRepository()


@router.get("/", response_model=List[Transaction])
async def get_all_transactions(
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user)
):
    """
    Get all transactions.
    
    Args:
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        current_user: Currently authenticated user from token validation.
        
    Returns:
        List of transactions.
    """
    return await transaction_repo.list(skip=skip, limit=limit)


@router.get("/{transaction_id}", response_model=Transaction)
async def get_transaction(
    transaction_id: UUID = Path(..., description="The ID of the transaction to retrieve"),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific transaction by ID.
    
    Args:
        transaction_id: The ID of the transaction to retrieve
        current_user: Currently authenticated user from token validation.
        
    Returns:
        The transaction if found.
    """
    transaction = await transaction_repo.get(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found"
        )
    return transaction


@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: Transaction,
    current_user: User = Depends(get_current_user),
    process_for_anomalies: bool = Query(True, description="Whether to preprocess the transaction for anomaly detection")
):
    """
    [OWL: fleetsight-anomaly.ttl#AnomalyDetectionProcess]
    
    Create a new transaction with optional preprocessing for anomaly detection.
    
    Args:
        transaction: The transaction data to create
        current_user: Currently authenticated user from token validation
        process_for_anomalies: Flag to preprocess transaction for anomaly detection
        
    Returns:
        The created transaction and processed data if requested.
    """
    # Save the transaction
    created_transaction = await transaction_repo.create(transaction)
    
    result = {"transaction": created_transaction}
    
    if process_for_anomalies:
        # Get transaction history for the vehicle if available
        transaction_history = []
        if transaction.vehicle_id:
            transaction_history = await transaction_repo.find_by_vehicle(transaction.vehicle_id)
        
        # Preprocess the transaction for anomaly detection
        processed_data = preprocess_data(transaction, transaction_history)
        result["processed_data"] = processed_data
    
    return result


@router.post("/batch", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_transactions_batch(
    transactions: List[Transaction] = Body(..., description="List of transactions to create"),
    current_user: User = Depends(get_current_user),
    process_for_anomalies: bool = Query(True, description="Whether to preprocess the transactions for anomaly detection")
):
    """
    [OWL: fleetsight-anomaly.ttl#BatchAnomalyDetectionProcess]
    
    Create multiple transactions in a batch with optional preprocessing for anomaly detection.
    
    Args:
        transactions: List of transaction data to create
        current_user: Currently authenticated user from token validation
        process_for_anomalies: Flag to preprocess transactions for anomaly detection
        
    Returns:
        The created transactions and processed data if requested.
    """
    if not transactions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No transactions provided"
        )
    
    created_transactions = []
    processed_transactions = []
    
    # Get all transaction history once for efficiency
    vehicle_history_map = {}
    if process_for_anomalies:
        # Get unique vehicle IDs
        vehicle_ids = {t.vehicle_id for t in transactions if t.vehicle_id}
        
        # Fetch transaction history for each vehicle
        for vehicle_id in vehicle_ids:
            vehicle_history_map[vehicle_id] = await transaction_repo.find_by_vehicle(vehicle_id)
    
    # Process each transaction
    for transaction in transactions:
        # Save the transaction
        created_transaction = await transaction_repo.create(transaction)
        created_transactions.append(created_transaction)
        
        if process_for_anomalies:
            # Get transaction history for this vehicle if available
            transaction_history = vehicle_history_map.get(transaction.vehicle_id, [])
            
            # Preprocess the transaction for anomaly detection
            processed_data = preprocess_data(transaction, transaction_history)
            processed_transactions.append(processed_data)
    
    result = {
        "created": len(created_transactions),
        "transactions": created_transactions
    }
    
    if process_for_anomalies:
        result["processed_data"] = processed_transactions
    
    return result


@router.put("/{transaction_id}", response_model=Dict[str, Any])
async def update_transaction(
    transaction_id: UUID = Path(..., description="The ID of the transaction to update"),
    transaction: Transaction = Body(..., description="Updated transaction data"),
    current_user: User = Depends(get_current_user),
    process_for_anomalies: bool = Query(True, description="Whether to preprocess the updated transaction for anomaly detection")
):
    """
    [OWL: fleetsight-anomaly.ttl#AnomalyDetectionProcess]
    
    Update a transaction with optional preprocessing for anomaly detection.
    
    Args:
        transaction_id: The ID of the transaction to update
        transaction: The updated transaction data
        current_user: Currently authenticated user from token validation
        process_for_anomalies: Flag to preprocess transaction for anomaly detection
        
    Returns:
        The updated transaction and processed data if requested.
    """
    # Check if transaction exists
    existing_transaction = await transaction_repo.get(transaction_id)
    if not existing_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found"
        )
    
    # Update the transaction
    updated_transaction = await transaction_repo.update(transaction_id, transaction)
    
    result = {"transaction": updated_transaction}
    
    if process_for_anomalies:
        # Get transaction history for the vehicle if available
        transaction_history = []
        if updated_transaction.vehicle_id:
            transaction_history = await transaction_repo.find_by_vehicle(updated_transaction.vehicle_id)
        
        # Preprocess the transaction for anomaly detection
        processed_data = preprocess_data(updated_transaction, transaction_history)
        result["processed_data"] = processed_data
    
    return result


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: UUID = Path(..., description="The ID of the transaction to delete"),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a transaction.
    
    Args:
        transaction_id: The ID of the transaction to delete
        current_user: Currently authenticated user from token validation.
        
    Returns:
        No content on successful deletion.
    """
    # Check if transaction exists
    existing_transaction = await transaction_repo.get(transaction_id)
    if not existing_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found"
        )
    
    # Delete the transaction
    success = await transaction_repo.delete(transaction_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete transaction"
        )
    return None


@router.get("/driver/{driver_id}", response_model=List[Transaction])
async def get_transactions_by_driver(
    driver_id: UUID = Path(..., description="The ID of the driver to filter by"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user)
):
    """
    Get transactions for a specific driver.
    
    Args:
        driver_id: The ID of the driver to filter by
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        current_user: Currently authenticated user from token validation.
        
    Returns:
        List of transactions for the specified driver.
    """
    return await transaction_repo.find_by_driver(driver_id, skip=skip, limit=limit)


@router.get("/vehicle/{vehicle_id}", response_model=List[Transaction])
async def get_transactions_by_vehicle(
    vehicle_id: UUID = Path(..., description="The ID of the vehicle to filter by"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user)
):
    """
    Get transactions for a specific vehicle.
    
    Args:
        vehicle_id: The ID of the vehicle to filter by
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        current_user: Currently authenticated user from token validation.
        
    Returns:
        List of transactions for the specified vehicle.
    """
    return await transaction_repo.find_by_vehicle(vehicle_id, skip=skip, limit=limit)


@router.get("/date-range/", response_model=List[Transaction])
async def get_transactions_by_date_range(
    start_date: datetime = Query(..., description="Start date for filtering transactions"),
    end_date: datetime = Query(..., description="End date for filtering transactions"),
    skip: int = Query(0, description="Number of records to skip"),
    limit: int = Query(100, description="Maximum number of records to return"),
    current_user: User = Depends(get_current_user)
):
    """
    Get transactions within a date range.
    
    Args:
        start_date: Start date for filtering transactions
        end_date: End date for filtering transactions
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        current_user: Currently authenticated user from token validation.
        
    Returns:
        List of transactions within the specified date range.
    """
    return await transaction_repo.find_by_date_range(
        start_date=start_date, 
        end_date=end_date,
        skip=skip,
        limit=limit
    )


@router.post("/process/{transaction_id}", response_model=ProcessedTransaction)
async def process_transaction(
    transaction_id: UUID = Path(..., description="The ID of the transaction to process"),
    current_user: User = Depends(get_current_user)
):
    """
    [OWL: fleetsight-anomaly.ttl#AnomalyDetectionProcess]
    
    Process an existing transaction for anomaly detection.
    
    This endpoint allows manually triggering the preprocessing pipeline
    for an existing transaction, which is useful for testing or
    reprocessing historical data.
    
    Args:
        transaction_id: The ID of the transaction to process
        current_user: Currently authenticated user from token validation
        
    Returns:
        The processed transaction data
    """
    # Get the transaction
    transaction = await transaction_repo.get(transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction with ID {transaction_id} not found"
        )
    
    # Get transaction history for the vehicle if available
    transaction_history = []
    if transaction.vehicle_id:
        transaction_history = await transaction_repo.find_by_vehicle(transaction.vehicle_id)
    
    # Preprocess the transaction for anomaly detection
    processed_data = preprocess_data(transaction, transaction_history)
    
    return processed_data 