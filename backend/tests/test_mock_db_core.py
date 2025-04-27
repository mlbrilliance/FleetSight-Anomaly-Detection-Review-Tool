"""
Tests for the MockDB Core implementation.
[OWL: fleetsight-system.ttl#TestSuite]

This module tests the MockDB core functionality including
connection lifecycle and transaction management.
"""
import pytest
import pytest_asyncio
from decimal import Decimal

from shared_models.models import Vehicle
from backend.db.mock_db import MockDB

@pytest_asyncio.fixture
async def mock_db():
    """Create and initialize a MockDB instance for testing."""
    db = MockDB()
    await db.connect()
    yield db
    await db.disconnect()


class TestMockDBCore:
    """Test basic MockDB operations and transaction handling."""
    
    @pytest.mark.asyncio
    async def test_connection_lifecycle(self):
        """Test database connection/disconnection."""
        db = MockDB()
        await db.connect()
        assert await db.health_check() is True
        await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_transaction_commit(self, mock_db):
        """Test transaction commit functionality."""
        # Create a new vehicle outside of transaction
        vehicle_before_tx = Vehicle(
            vehicle_id="TX_TEST_V1",
            make="Ford",
            model="Mustang",
            year=2022,
            vehicle_type="Sports",
            fuel_capacity=Decimal("16.0"),
            fuel_capacity_unit="gallon"
        )
        
        # Start a transaction
        await mock_db.begin_transaction()
        
        # Create vehicle in transaction
        await mock_db.create_vehicle(vehicle_before_tx)
        
        # Create another vehicle that will be committed
        vehicle_in_tx = Vehicle(
            vehicle_id="TX_TEST_V2",
            make="Chevrolet",
            model="Corvette",
            year=2023,
            vehicle_type="Sports",
            fuel_capacity=Decimal("18.5"),
            fuel_capacity_unit="gallon"
        )
        await mock_db.create_vehicle(vehicle_in_tx)
        
        # Commit the transaction
        await mock_db.commit_transaction()
        
        # Verify both vehicles exist
        saved_v1 = await mock_db.get_vehicle_by_id("TX_TEST_V1")
        saved_v2 = await mock_db.get_vehicle_by_id("TX_TEST_V2")
        
        assert saved_v1 is not None
        assert saved_v2 is not None
        assert saved_v1.make == "Ford"
        assert saved_v2.make == "Chevrolet"
    
    @pytest.mark.asyncio
    async def test_transaction_rollback(self, mock_db):
        """Test transaction rollback functionality."""
        # Create a vehicle outside of transaction that should persist
        persist_vehicle = Vehicle(
            vehicle_id="TX_PERSIST",
            make="Toyota",
            model="Corolla",
            year=2021,
            vehicle_type="Sedan",
            fuel_capacity=Decimal("13.2"),
            fuel_capacity_unit="gallon"
        )
        await mock_db.create_vehicle(persist_vehicle)
        
        # Start a transaction
        await mock_db.begin_transaction()
        
        # Create a vehicle in the transaction
        rollback_vehicle = Vehicle(
            vehicle_id="TX_ROLLBACK",
            make="Honda",
            model="Civic",
            year=2022,
            vehicle_type="Sedan",
            fuel_capacity=Decimal("12.4"),
            fuel_capacity_unit="gallon"
        )
        await mock_db.create_vehicle(rollback_vehicle)
        
        # Update the persisted vehicle
        updated_vehicle = Vehicle(
            vehicle_id="TX_PERSIST",
            make="Toyota",
            model="Corolla UPDATED",
            year=2021,
            vehicle_type="Sedan",
            fuel_capacity=Decimal("13.2"),
            fuel_capacity_unit="gallon"
        )
        await mock_db.update_vehicle(updated_vehicle)
        
        # Verify temporary updates visible within transaction
        during_tx = await mock_db.get_vehicle_by_id("TX_PERSIST")
        assert during_tx.model == "Corolla UPDATED"
        
        # Now rollback the transaction
        await mock_db.rollback_transaction()
        
        # The rollback vehicle should not exist
        assert await mock_db.get_vehicle_by_id("TX_ROLLBACK") is None
        
        # The persisted vehicle should have original values
        after_rollback = await mock_db.get_vehicle_by_id("TX_PERSIST")
        assert after_rollback is not None
        assert after_rollback.model == "Corolla" 