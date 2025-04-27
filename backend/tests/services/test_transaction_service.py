"""
Tests for the transaction service.
"""

import pytest
from datetime import datetime

from backend.models.transaction import TransactionCreate, TransactionUpdate
from backend.services.transaction_service import TransactionService


@pytest.mark.asyncio
async def test_get_transactions(mock_supabase):
    """Test getting all transactions."""
    service = TransactionService()
    transactions = await service.get_transactions()
    
    assert len(transactions) == 1
    assert transactions[0].vehicle_id == "123e4567-e89b-12d3-a456-426614174003"
    assert transactions[0].type == "fuel"
    assert transactions[0].amount == 50.00


@pytest.mark.asyncio
async def test_get_transaction(mock_supabase):
    """Test getting a specific transaction."""
    service = TransactionService()
    transaction = await service.get_transaction("123e4567-e89b-12d3-a456-426614174005")
    
    assert transaction is not None
    assert transaction.id == "123e4567-e89b-12d3-a456-426614174005"
    assert transaction.vehicle_id == "123e4567-e89b-12d3-a456-426614174003"
    assert transaction.type == "fuel"
    assert transaction.amount == 50.00


@pytest.mark.asyncio
async def test_get_nonexistent_transaction(mock_supabase):
    """Test getting a nonexistent transaction."""
    service = TransactionService()
    transaction = await service.get_transaction("non-existent-id")
    
    assert transaction is None


@pytest.mark.asyncio
async def test_create_transaction(mock_supabase):
    """Test creating a new transaction."""
    service = TransactionService()
    new_transaction = TransactionCreate(
        vehicle_id="123e4567-e89b-12d3-a456-426614174003",
        driver_id="123e4567-e89b-12d3-a456-426614174004",
        type="maintenance",
        amount=120.50,
        date=datetime.fromisoformat("2023-05-20T10:30:00+00:00"),
        description="Oil change and filter replacement",
        receipt_url="https://example.com/receipts/maintenance123.jpg",
        odometer_reading=12500.5,
        location="Service Center"
    )
    
    created_transaction = await service.create_transaction(new_transaction)
    
    assert created_transaction is not None
    assert created_transaction.vehicle_id == "123e4567-e89b-12d3-a456-426614174003"
    assert created_transaction.driver_id == "123e4567-e89b-12d3-a456-426614174004"
    assert created_transaction.type == "maintenance"
    assert created_transaction.amount == 120.50
    assert created_transaction.description == "Oil change and filter replacement"
    
    # Check if the transaction was added to the database
    all_transactions = await service.get_transactions()
    assert len(all_transactions) == 2


@pytest.mark.asyncio
async def test_update_transaction(mock_supabase):
    """Test updating a transaction."""
    service = TransactionService()
    transaction_id = "123e4567-e89b-12d3-a456-426614174005"
    
    update_data = TransactionUpdate(
        amount=55.75,
        description="Updated fuel transaction",
        receipt_url="https://example.com/receipts/updated-fuel.jpg"
    )
    
    updated_transaction = await service.update_transaction(transaction_id, update_data)
    
    assert updated_transaction is not None
    assert updated_transaction.id == transaction_id
    assert updated_transaction.amount == 55.75
    assert updated_transaction.description == "Updated fuel transaction"
    assert updated_transaction.receipt_url == "https://example.com/receipts/updated-fuel.jpg"
    
    # Check if the transaction was updated in the database
    transaction = await service.get_transaction(transaction_id)
    assert transaction.amount == 55.75
    assert transaction.description == "Updated fuel transaction"
    assert transaction.receipt_url == "https://example.com/receipts/updated-fuel.jpg"


@pytest.mark.asyncio
async def test_update_nonexistent_transaction(mock_supabase):
    """Test updating a nonexistent transaction."""
    service = TransactionService()
    
    update_data = TransactionUpdate(
        amount=55.75,
        description="Updated transaction"
    )
    
    updated_transaction = await service.update_transaction("non-existent-id", update_data)
    
    assert updated_transaction is None


@pytest.mark.asyncio
async def test_delete_transaction(mock_supabase):
    """Test deleting a transaction."""
    service = TransactionService()
    transaction_id = "123e4567-e89b-12d3-a456-426614174005"
    
    # Verify the transaction exists before deletion
    transaction_before = await service.get_transaction(transaction_id)
    assert transaction_before is not None
    
    # Delete the transaction
    result = await service.delete_transaction(transaction_id)
    assert result is True
    
    # Verify the transaction no longer exists
    transaction_after = await service.get_transaction(transaction_id)
    assert transaction_after is None


@pytest.mark.asyncio
async def test_delete_nonexistent_transaction(mock_supabase):
    """Test deleting a nonexistent transaction."""
    service = TransactionService()
    
    result = await service.delete_transaction("non-existent-id")
    assert result is False


@pytest.mark.asyncio
async def test_get_transactions_by_vehicle(mock_supabase):
    """Test getting transactions by vehicle ID."""
    service = TransactionService()
    vehicle_id = "123e4567-e89b-12d3-a456-426614174003"
    
    transactions = await service.get_transactions_by_vehicle(vehicle_id)
    
    assert len(transactions) == 1
    assert transactions[0].vehicle_id == vehicle_id
    assert transactions[0].type == "fuel"
    
    # Test with nonexistent vehicle ID
    transactions = await service.get_transactions_by_vehicle("non-existent-vehicle")
    assert len(transactions) == 0


@pytest.mark.asyncio
async def test_get_transactions_by_driver(mock_supabase):
    """Test getting transactions by driver ID."""
    service = TransactionService()
    driver_id = "123e4567-e89b-12d3-a456-426614174004"
    
    transactions = await service.get_transactions_by_driver(driver_id)
    
    assert len(transactions) == 1
    assert transactions[0].driver_id == driver_id
    assert transactions[0].type == "fuel"
    
    # Test with nonexistent driver ID
    transactions = await service.get_transactions_by_driver("non-existent-driver")
    assert len(transactions) == 0


@pytest.mark.asyncio
async def test_get_transactions_by_type(mock_supabase):
    """Test getting transactions by type."""
    service = TransactionService()
    
    # Test with existing type
    transactions = await service.get_transactions_by_type("fuel")
    assert len(transactions) == 1
    assert transactions[0].type == "fuel"
    
    # Test with nonexistent type
    transactions = await service.get_transactions_by_type("non-existent-type")
    assert len(transactions) == 0


@pytest.mark.asyncio
async def test_get_transactions_by_date_range(mock_supabase):
    """Test getting transactions by date range."""
    service = TransactionService()
    
    # Set up date range
    start_date = datetime.fromisoformat("2023-01-01T00:00:00+00:00")
    end_date = datetime.fromisoformat("2023-12-31T23:59:59+00:00")
    
    # Test with date range that includes transactions
    transactions = await service.get_transactions_by_date_range(start_date, end_date)
    assert len(transactions) == 1
    
    # Test with date range that doesn't include transactions
    start_date = datetime.fromisoformat("2022-01-01T00:00:00+00:00")
    end_date = datetime.fromisoformat("2022-12-31T23:59:59+00:00")
    transactions = await service.get_transactions_by_date_range(start_date, end_date)
    assert len(transactions) == 0 