"""
Test module for transaction operations in the MockDB implementation.

This module tests the CRUD operations for transactions in the 
MockDB implementation, ensuring that the TransactionRepository
interface is properly implemented.
"""
import pytest
import pytest_asyncio
from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from typing import List

from backend.db.mock_db import MockDB
from shared_models.models import FleetTransaction, Vehicle
from backend.db.interface import TransactionRepository

@pytest_asyncio.fixture
async def mock_db():
    """Initialize and return a MockDB instance for testing."""
    db = MockDB()
    await db.connect()
    yield db
    await db.disconnect()

class TestTransactionRepository:
    """Test the TransactionRepository implementation in MockDB."""

    @pytest.mark.asyncio
    async def test_create_transaction(self, mock_db):
        """Test creating a transaction in the database."""
        transaction = FleetTransaction(
            transaction_id=str(uuid4()),
            timestamp=datetime.now(),
            amount=Decimal("100.50"),
            currency="USD",
            merchant_name="Test Merchant",
            merchant_category="Testing"
        )
        
        # Create the transaction
        created_transaction = await mock_db.create_transaction(transaction)
        
        # Verify the transaction was created
        assert created_transaction is not None
        assert created_transaction.transaction_id == transaction.transaction_id
        assert created_transaction.amount == transaction.amount
        
        # Verify it exists in the database
        stored_transaction = await mock_db.get_transaction_by_id(transaction.transaction_id)
        assert stored_transaction is not None
        assert stored_transaction.transaction_id == transaction.transaction_id
    
    @pytest.mark.asyncio
    async def test_update_transaction(self, mock_db):
        """Test updating a transaction in the database."""
        # Create a transaction first
        transaction = FleetTransaction(
            transaction_id=str(uuid4()),
            timestamp=datetime.now(),
            amount=Decimal("100.50"),
            currency="USD",
            merchant_name="Test Merchant",
            merchant_category="Testing"
        )
        
        created_transaction = await mock_db.create_transaction(transaction)
        
        # Update the transaction
        updated_amount = Decimal("150.75")
        created_transaction.amount = updated_amount
        created_transaction.merchant_name = "Updated Merchant"
        
        updated_transaction = await mock_db.update_transaction(created_transaction)
        
        # Verify the update was successful
        assert updated_transaction is not None
        assert updated_transaction.transaction_id == transaction.transaction_id
        assert updated_transaction.amount == updated_amount
        assert updated_transaction.merchant_name == "Updated Merchant"
        
        # Verify the changes persist in the database
        stored_transaction = await mock_db.get_transaction_by_id(transaction.transaction_id)
        assert stored_transaction is not None
        assert stored_transaction.amount == updated_amount
        assert stored_transaction.merchant_name == "Updated Merchant"
    
    @pytest.mark.asyncio
    async def test_get_transactions_by_vehicle(self, mock_db):
        """Test retrieving transactions associated with a specific vehicle."""
        # Create a vehicle first
        vehicle = Vehicle(
            vehicle_id="TEST-VEH-1",
            make="Test Make",
            model="Test Model",
            year=2023,
            vehicle_type="Test",
            fuel_capacity=Decimal("60.0"),
            fuel_capacity_unit="L"
        )
        
        await mock_db.create_vehicle(vehicle)
        
        # Create another vehicle for the third transaction
        another_vehicle = Vehicle(
            vehicle_id="ANOTHER-VEHICLE",
            make="Another Make",
            model="Another Model",
            year=2022,
            vehicle_type="Test",
            fuel_capacity=Decimal("50.0"),
            fuel_capacity_unit="L"
        )
        
        await mock_db.create_vehicle(another_vehicle)
        
        # Create several transactions with different vehicle_ids
        transaction1 = FleetTransaction(
            transaction_id=str(uuid4()),
            timestamp=datetime.now(),
            amount=Decimal("100.50"),
            currency="USD",
            merchant_name="Test Merchant 1",
            merchant_category="Testing",
            vehicle_id=vehicle.vehicle_id
        )
        
        transaction2 = FleetTransaction(
            transaction_id=str(uuid4()),
            timestamp=datetime.now(),
            amount=Decimal("200.75"),
            currency="USD",
            merchant_name="Test Merchant 2",
            merchant_category="Testing",
            vehicle_id=vehicle.vehicle_id
        )
        
        transaction3 = FleetTransaction(
            transaction_id=str(uuid4()),
            timestamp=datetime.now(),
            amount=Decimal("300.25"),
            currency="USD",
            merchant_name="Test Merchant 3",
            merchant_category="Testing",
            vehicle_id=another_vehicle.vehicle_id
        )
        
        await mock_db.create_transaction(transaction1)
        await mock_db.create_transaction(transaction2)
        await mock_db.create_transaction(transaction3)
        
        # Retrieve transactions for the test vehicle
        vehicle_transactions = await mock_db.get_transactions_by_vehicle(vehicle.vehicle_id)
        
        # Verify we got the correct transactions
        assert len(vehicle_transactions) == 2
        assert all(t.vehicle_id == vehicle.vehicle_id for t in vehicle_transactions)
        
        # Verify transactions for a non-existent vehicle
        non_existent = await mock_db.get_transactions_by_vehicle("NON-EXISTENT")
        assert len(non_existent) == 0
    
    @pytest.mark.asyncio
    async def test_get_all_transactions(self, mock_db):
        """Test retrieving all transactions with pagination."""
        # Get initial count to validate our additions
        initial_transactions = await mock_db.get_transactions_by_filter({})
        initial_count = len(initial_transactions)
        
        # Create several test transactions
        test_transaction_ids = []
        for i in range(5):
            transaction = FleetTransaction(
                transaction_id=f"TRANS-{i}",
                timestamp=datetime.now(),
                amount=Decimal(f"{100 + i}.50"),
                currency="USD",
                merchant_name=f"Test Merchant {i}",
                merchant_category="Testing"
            )
            await mock_db.create_transaction(transaction)
            test_transaction_ids.append(f"TRANS-{i}")
        
        # Test retrieving all transactions using get_transactions_by_filter with empty filter
        all_transactions = await mock_db.get_transactions_by_filter({})
        assert len(all_transactions) == initial_count + 5
        
        # Test that our new transactions are in the results
        transaction_ids = [t.transaction_id for t in all_transactions]
        for test_id in test_transaction_ids:
            assert test_id in transaction_ids
    
    @pytest.mark.asyncio
    async def test_delete_transaction(self, mock_db):
        """Test deleting a transaction from the database."""
        # Create a transaction
        transaction = FleetTransaction(
            transaction_id=str(uuid4()),
            timestamp=datetime.now(),
            amount=Decimal("100.50"),
            currency="USD",
            merchant_name="Test Merchant",
            merchant_category="Testing"
        )
        
        created_transaction = await mock_db.create_transaction(transaction)
        
        # Verify it exists
        stored_transaction = await mock_db.get_transaction_by_id(transaction.transaction_id)
        assert stored_transaction is not None
        
        # Delete the transaction
        result = await mock_db.delete_transaction(transaction.transaction_id)
        assert result is True
        
        # Verify it's been deleted
        deleted_transaction = await mock_db.get_transaction_by_id(transaction.transaction_id)
        assert deleted_transaction is None
        
        # Try to delete a non-existent transaction
        result = await mock_db.delete_transaction("NON-EXISTENT")
        assert result is False 