"""
Tests for the transaction service.
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import patch, MagicMock

from backend.models.transaction import Transaction, TransactionCreate, TransactionUpdate
from backend.services.transaction_service import TransactionService


@pytest.mark.asyncio
async def test_get_all_transactions(mock_supabase):
    """Test getting all transactions."""
    # Arrange
    transaction_service = TransactionService()
    
    # Act
    transactions = await transaction_service.get_all_transactions()
    
    # Assert
    assert len(transactions) == 1
    assert transactions[0].id == "123e4567-e89b-12d3-a456-426614174004"
    assert transactions[0].transaction_type == "fuel"
    assert transactions[0].amount == 75.50
    assert transactions[0].driver_id == "123e4567-e89b-12d3-a456-426614174000"
    assert transactions[0].vehicle_id == "123e4567-e89b-12d3-a456-426614174001"


@pytest.mark.asyncio
async def test_get_transaction_by_id(mock_supabase):
    """Test getting a transaction by ID."""
    # Arrange
    transaction_service = TransactionService()
    transaction_id = "123e4567-e89b-12d3-a456-426614174004"
    
    # Act
    transaction = await transaction_service.get_transaction_by_id(transaction_id)
    
    # Assert
    assert transaction is not None
    assert transaction.id == transaction_id
    assert transaction.transaction_type == "fuel"
    assert transaction.amount == 75.50
    assert transaction.location == "Gas Station A"
    assert transaction.odometer_reading == 15250


@pytest.mark.asyncio
async def test_get_transaction_by_id_not_found(mock_supabase):
    """Test getting a transaction by ID when the transaction doesn't exist."""
    # Arrange
    transaction_service = TransactionService()
    transaction_id = "non-existent-id"
    
    # Configure the mock to return empty data for this ID
    with patch('backend.db.supabase_client.get_supabase_client') as mock_get_client:
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_table.select.return_value.__aenter__.return_value = MagicMock(data=[])
        mock_client.table.return_value = mock_table
        mock_get_client.return_value = mock_client
        
        # Act/Assert
        with pytest.raises(ValueError, match="Transaction not found"):
            await transaction_service.get_transaction_by_id(transaction_id)


@pytest.mark.asyncio
async def test_create_transaction(mock_supabase):
    """Test creating a transaction."""
    # Arrange
    transaction_service = TransactionService()
    transaction_create = TransactionCreate(
        fleet_id="123e4567-e89b-12d3-a456-426614174002",
        vehicle_id="123e4567-e89b-12d3-a456-426614174001",
        driver_id="123e4567-e89b-12d3-a456-426614174000",
        transaction_type="maintenance",
        amount=150.00,
        date=datetime.now().date(),
        location="Auto Repair Shop",
        odometer_reading=15500,
        payment_method="company_card",
        reference_number="MAINT12345",
        notes="Regular oil change and tire rotation"
    )
    
    # Act
    new_transaction = await transaction_service.create_transaction(transaction_create)
    
    # Assert
    assert new_transaction is not None
    assert new_transaction.id is not None
    assert new_transaction.transaction_type == "maintenance"
    assert new_transaction.amount == 150.00
    assert new_transaction.location == "Auto Repair Shop"
    assert new_transaction.odometer_reading == 15500


@pytest.mark.asyncio
async def test_update_transaction(mock_supabase):
    """Test updating a transaction."""
    # Arrange
    transaction_service = TransactionService()
    transaction_id = "123e4567-e89b-12d3-a456-426614174004"
    transaction_update = TransactionUpdate(
        amount=80.50,
        odometer_reading=15275,
        notes="Updated fuel transaction with corrected amount"
    )
    
    # Act
    updated_transaction = await transaction_service.update_transaction(transaction_id, transaction_update)
    
    # Assert
    assert updated_transaction is not None
    assert updated_transaction.id == transaction_id
    assert updated_transaction.amount == 80.50
    assert updated_transaction.odometer_reading == 15275
    assert updated_transaction.notes == "Updated fuel transaction with corrected amount"


@pytest.mark.asyncio
async def test_delete_transaction(mock_supabase):
    """Test deleting a transaction."""
    # Arrange
    transaction_service = TransactionService()
    transaction_id = "123e4567-e89b-12d3-a456-426614174004"
    
    # Act
    result = await transaction_service.delete_transaction(transaction_id)
    
    # Assert
    assert result is True


@pytest.mark.asyncio
async def test_get_transactions_by_fleet(mock_supabase):
    """Test getting transactions by fleet ID."""
    # Arrange
    transaction_service = TransactionService()
    fleet_id = "123e4567-e89b-12d3-a456-426614174002"
    
    # Act
    transactions = await transaction_service.get_transactions_by_fleet(fleet_id)
    
    # Assert
    assert len(transactions) == 1
    assert transactions[0].id == "123e4567-e89b-12d3-a456-426614174004"
    assert transactions[0].fleet_id == fleet_id


@pytest.mark.asyncio
async def test_get_transactions_by_vehicle(mock_supabase):
    """Test getting transactions by vehicle ID."""
    # Arrange
    transaction_service = TransactionService()
    vehicle_id = "123e4567-e89b-12d3-a456-426614174001"
    
    # Act
    transactions = await transaction_service.get_transactions_by_vehicle(vehicle_id)
    
    # Assert
    assert len(transactions) == 1
    assert transactions[0].id == "123e4567-e89b-12d3-a456-426614174004"
    assert transactions[0].vehicle_id == vehicle_id


@pytest.mark.asyncio
async def test_get_transactions_by_driver(mock_supabase):
    """Test getting transactions by driver ID."""
    # Arrange
    transaction_service = TransactionService()
    driver_id = "123e4567-e89b-12d3-a456-426614174000"
    
    # Act
    transactions = await transaction_service.get_transactions_by_driver(driver_id)
    
    # Assert
    assert len(transactions) == 1
    assert transactions[0].id == "123e4567-e89b-12d3-a456-426614174004"
    assert transactions[0].driver_id == driver_id


@pytest.mark.asyncio
async def test_get_transactions_by_type(mock_supabase):
    """Test getting transactions by type."""
    # Arrange
    transaction_service = TransactionService()
    transaction_type = "fuel"
    
    # Act
    transactions = await transaction_service.get_transactions_by_type(transaction_type)
    
    # Assert
    assert len(transactions) == 1
    assert transactions[0].id == "123e4567-e89b-12d3-a456-426614174004"
    assert transactions[0].transaction_type == transaction_type 