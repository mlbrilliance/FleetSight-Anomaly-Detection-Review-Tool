"""
Tests for the MockDB implementation.
[OWL: fleetsight-system.ttl#TestSuite]

This module tests the MockDB implementation against its contracts and
validates OWL ontology compliance.
"""
import asyncio
import pytest
import pytest_asyncio
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

from shared_models.models import (
    FleetTransaction, FuelTransaction, MaintenanceTransaction,
    Vehicle, Driver
)

from backend.db.mock_db import MockDB
from backend.db.interface import (
    TransactionRepository, VehicleRepository, DriverRepository
)

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


class TestVehicleRepository:
    """Test MockDB's VehicleRepository implementation."""
    
    @pytest.mark.asyncio
    async def test_create_vehicle(self, mock_db):
        """Test vehicle creation."""
        new_vehicle = Vehicle(
            vehicle_id="TEST_V1",
            make="Tesla",
            model="Model S",
            year=2022,
            vehicle_type="EV",
            fuel_capacity=Decimal("100.0"),
            fuel_capacity_unit="kWh"
        )
        
        created = await mock_db.create_vehicle(new_vehicle)
        assert created.vehicle_id == "TEST_V1"
        assert created.make == "Tesla"
        
        # Verify created in storage
        saved = await mock_db.get_vehicle_by_id("TEST_V1")
        assert saved is not None
        assert saved.model == "Model S"
        assert saved.year == 2022
    
    @pytest.mark.asyncio
    async def test_update_vehicle(self, mock_db):
        """Test vehicle update."""
        # Create a vehicle first
        original = Vehicle(
            vehicle_id="UPDATE_V1",
            make="Subaru",
            model="Outback",
            year=2020,
            vehicle_type="SUV",
            fuel_capacity=Decimal("18.5"),
            fuel_capacity_unit="gallon"
        )
        await mock_db.create_vehicle(original)
        
        # Update it
        updated = Vehicle(
            vehicle_id="UPDATE_V1",
            make="Subaru",
            model="Outback",
            year=2021,  # Changed year
            vehicle_type="Crossover",  # Changed type
            fuel_capacity=Decimal("18.5"),
            fuel_capacity_unit="gallon"
        )
        result = await mock_db.update_vehicle(updated)
        
        # Verify updated
        assert result.year == 2021
        assert result.vehicle_type == "Crossover"
        
        # Verify in storage
        saved = await mock_db.get_vehicle_by_id("UPDATE_V1")
        assert saved is not None
        assert saved.year == 2021
        assert saved.vehicle_type == "Crossover"
    
    @pytest.mark.asyncio
    async def test_get_all_vehicles(self, mock_db):
        """Test retrieval of all vehicles with pagination."""
        # The mock DB already has vehicles from _populate_test_data
        vehicles = await mock_db.get_all_vehicles()
        
        # Check we have the expected number of pre-populated vehicles
        assert len(vehicles) >= 3  # We expect at least 3 from test data
        
        # Test pagination
        first_page = await mock_db.get_all_vehicles(limit=2, offset=0)
        second_page = await mock_db.get_all_vehicles(limit=2, offset=2)
        
        assert len(first_page) == 2
        assert len(second_page) > 0  # Could be less than 2 depending on total count
        
        # Verify different pages return different vehicles
        assert first_page[0].vehicle_id != second_page[0].vehicle_id
    
    @pytest.mark.asyncio
    async def test_delete_vehicle(self, mock_db):
        """Test vehicle deletion."""
        # Create a vehicle to delete
        delete_vehicle = Vehicle(
            vehicle_id="DELETE_V1",
            make="Nissan",
            model="Leaf",
            year=2019,
            vehicle_type="EV",
            fuel_capacity=Decimal("40.0"),
            fuel_capacity_unit="kWh"
        )
        await mock_db.create_vehicle(delete_vehicle)
        
        # Verify it exists
        assert await mock_db.get_vehicle_by_id("DELETE_V1") is not None
        
        # Delete it
        result = await mock_db.delete_vehicle("DELETE_V1")
        assert result is True
        
        # Verify it's gone
        assert await mock_db.get_vehicle_by_id("DELETE_V1") is None
        
        # Deleting non-existent should return False
        result = await mock_db.delete_vehicle("NONEXISTENT")
        assert result is False


class TestDriverRepository:
    """Test MockDB's DriverRepository implementation."""
    
    @pytest.mark.asyncio
    async def test_create_driver(self, mock_db):
        """Test driver creation."""
        new_driver = Driver(
            driver_id="TEST_D1",
            name="Test Driver",
            license_number="DL987654",
            assigned_vehicle_ids=["V001"]  # Assuming V001 exists in test data
        )
        
        created = await mock_db.create_driver(new_driver)
        assert created.driver_id == "TEST_D1"
        assert created.name == "Test Driver"
        
        # Verify created in storage
        saved = await mock_db.get_driver_by_id("TEST_D1")
        assert saved is not None
        assert saved.license_number == "DL987654"
        assert "V001" in saved.assigned_vehicle_ids
    
    @pytest.mark.asyncio
    async def test_update_driver(self, mock_db):
        """Test driver update."""
        # Create a driver first
        original = Driver(
            driver_id="UPDATE_D1",
            name="Update Driver",
            license_number="DL555555"
        )
        await mock_db.create_driver(original)
        
        # Update it
        updated = Driver(
            driver_id="UPDATE_D1",
            name="Updated Name",  # Changed name
            license_number="DL555555",
            assigned_vehicle_ids=["V002"]  # Added vehicle assignment
        )
        result = await mock_db.update_driver(updated)
        
        # Verify updated
        assert result.name == "Updated Name"
        assert "V002" in result.assigned_vehicle_ids
        
        # Verify in storage
        saved = await mock_db.get_driver_by_id("UPDATE_D1")
        assert saved is not None
        assert saved.name == "Updated Name"
        assert "V002" in saved.assigned_vehicle_ids
    
    @pytest.mark.asyncio
    async def test_get_all_drivers(self, mock_db):
        """Test retrieval of all drivers with pagination."""
        # The mock DB already has drivers from _populate_test_data
        drivers = await mock_db.get_all_drivers()
        
        # Check we have the expected number of pre-populated drivers
        assert len(drivers) >= 3  # We expect at least 3 from test data
        
        # Test pagination
        first_page = await mock_db.get_all_drivers(limit=2, offset=0)
        second_page = await mock_db.get_all_drivers(limit=2, offset=2)
        
        assert len(first_page) == 2
        assert len(second_page) > 0  # Could be less than 2 depending on total count
    
    @pytest.mark.asyncio
    async def test_get_drivers_by_vehicle(self, mock_db):
        """Test retrieving drivers assigned to a specific vehicle."""
        # Create test data with known assignments
        vehicle_id = "VEHICLE_ASSIGNMENT_TEST"
        
        # Create a vehicle
        vehicle = Vehicle(
            vehicle_id=vehicle_id,
            make="Honda",
            model="CR-V",
            year=2021,
            vehicle_type="SUV",
            fuel_capacity=Decimal("14.0"),
            fuel_capacity_unit="gallon"
        )
        await mock_db.create_vehicle(vehicle)
        
        # Create drivers assigned to this vehicle
        driver1 = Driver(
            driver_id="DRIVER_WITH_VEHICLE_1",
            name="Driver One",
            assigned_vehicle_ids=[vehicle_id]
        )
        driver2 = Driver(
            driver_id="DRIVER_WITH_VEHICLE_2",
            name="Driver Two",
            assigned_vehicle_ids=[vehicle_id, "V001"]  # Multiple assignments
        )
        driver3 = Driver(
            driver_id="DRIVER_WITHOUT_VEHICLE",
            name="Driver Three",
            assigned_vehicle_ids=[]  # No assignments
        )
        
        await mock_db.create_driver(driver1)
        await mock_db.create_driver(driver2)
        await mock_db.create_driver(driver3)
        
        # Now test the function
        drivers = await mock_db.get_drivers_by_vehicle(vehicle_id)
        
        # Should return the two drivers assigned to our vehicle
        assert len(drivers) == 2
        driver_ids = {d.driver_id for d in drivers}
        assert "DRIVER_WITH_VEHICLE_1" in driver_ids
        assert "DRIVER_WITH_VEHICLE_2" in driver_ids
        assert "DRIVER_WITHOUT_VEHICLE" not in driver_ids
    
    @pytest.mark.asyncio
    async def test_delete_driver(self, mock_db):
        """Test driver deletion."""
        # Create a driver to delete
        delete_driver = Driver(
            driver_id="DELETE_D1",
            name="Delete Driver",
            license_number="DL999999"
        )
        await mock_db.create_driver(delete_driver)
        
        # Verify it exists
        assert await mock_db.get_driver_by_id("DELETE_D1") is not None
        
        # Delete it
        result = await mock_db.delete_driver("DELETE_D1")
        assert result is True
        
        # Verify it's gone
        assert await mock_db.get_driver_by_id("DELETE_D1") is None


class TestTransactionRepository:
    """Test MockDB's TransactionRepository implementation."""
    
    @pytest.mark.asyncio
    async def test_create_transaction(self, mock_db):
        """Test transaction creation."""
        # Create a new fuel transaction
        now = datetime.now()
        new_transaction = FuelTransaction(
            transaction_id="TEST_TXN_F1",
            timestamp=now,
            amount=Decimal("50.00"),
            currency="USD",
            merchant_name="Test Gas Station",
            merchant_category="Fuel",
            latitude=40.7128,
            longitude=-74.0060,
            vehicle_id="V001",  # Using existing vehicle from test data
            driver_id="D001",   # Using existing driver from test data
            fuel_type="Premium",
            fuel_volume=Decimal("10.5"),
            fuel_volume_unit="gallon",
            odometer_reading=15000
        )
        
        created = await mock_db.create_transaction(new_transaction)
        assert created.transaction_id == "TEST_TXN_F1"
        assert created.merchant_name == "Test Gas Station"
        
        # Verify created in storage
        saved = await mock_db.get_transaction_by_id("TEST_TXN_F1")
        assert saved is not None
        assert isinstance(saved, FuelTransaction)  # Verify type preserved
        assert saved.fuel_type == "Premium"
        assert saved.fuel_volume == Decimal("10.5")
    
    @pytest.mark.asyncio
    async def test_create_maintenance_transaction(self, mock_db):
        """Test maintenance transaction creation."""
        now = datetime.now()
        maint_txn = MaintenanceTransaction(
            transaction_id="TEST_TXN_M1",
            timestamp=now,
            amount=Decimal("250.00"),
            currency="USD",
            merchant_name="Test Repair Shop",
            merchant_category="Maintenance",
            latitude=34.0522,
            longitude=-118.2437,
            vehicle_id="V002",  # Using existing vehicle from test data
            driver_id="D002",   # Using existing driver from test data
            maintenance_type="Brake Service",
            odometer_reading=45000
        )
        
        created = await mock_db.create_transaction(maint_txn)
        assert created.transaction_id == "TEST_TXN_M1"
        assert created.maintenance_type == "Brake Service"
        
        # Verify created and type preserved
        saved = await mock_db.get_transaction_by_id("TEST_TXN_M1")
        assert saved is not None
        assert isinstance(saved, MaintenanceTransaction)
        assert saved.maintenance_type == "Brake Service"
    
    @pytest.mark.asyncio
    async def test_get_transactions_by_filter(self, mock_db):
        """Test filtering transactions."""
        # The mock DB already has transactions from _populate_test_data
        
        # Filter by merchant category
        fuel_txns = await mock_db.get_transactions_by_filter(
            filter_params={"merchant_category": "Fuel"}
        )
        assert len(fuel_txns) > 0
        for txn in fuel_txns:
            assert txn.merchant_category == "Fuel"
        
        # Filter by vehicle
        v001_txns = await mock_db.get_transactions_by_filter(
            filter_params={"vehicle_id": "V001"}
        )
        assert len(v001_txns) > 0
        for txn in v001_txns:
            assert txn.vehicle_id == "V001"
    
    @pytest.mark.asyncio
    async def test_get_fuel_transactions(self, mock_db):
        """Test retrieving only fuel transactions."""
        # Get all fuel transactions
        fuel_txns = await mock_db.get_fuel_transactions({})
        
        # Verify they are all FuelTransaction instances
        assert len(fuel_txns) > 0
        for txn in fuel_txns:
            assert isinstance(txn, FuelTransaction)
        
        # Filter by vehicle_id
        v001_fuel_txns = await mock_db.get_fuel_transactions({"vehicle_id": "V001"})
        for txn in v001_fuel_txns:
            assert isinstance(txn, FuelTransaction)
            assert txn.vehicle_id == "V001"
    
    @pytest.mark.asyncio
    async def test_get_transactions_by_vehicle(self, mock_db):
        """Test retrieving transactions for a specific vehicle."""
        # Get transactions for vehicle V001
        transactions = await mock_db.get_transactions_by_vehicle("V001")
        
        # Verify all transactions are for V001
        assert len(transactions) > 0
        for txn in transactions:
            assert txn.vehicle_id == "V001"
    
    @pytest.mark.asyncio
    async def test_get_transactions_by_driver(self, mock_db):
        """Test retrieving transactions for a specific driver."""
        # Get transactions for driver D001
        transactions = await mock_db.get_transactions_by_driver("D001")
        
        # Verify all transactions are for D001
        assert len(transactions) > 0
        for txn in transactions:
            assert txn.driver_id == "D001"
    
    @pytest.mark.asyncio
    async def test_batch_create_transactions(self, mock_db):
        """Test creating multiple transactions in a batch."""
        now = datetime.now()
        
        # Create a list of transactions
        transactions = [
            FuelTransaction(
                transaction_id=f"BATCH_F{i}",
                timestamp=now - timedelta(days=i),
                amount=Decimal(f"{40 + i}.00"),
                currency="USD",
                merchant_name=f"Batch Fuel Station {i}",
                merchant_category="Fuel",
                vehicle_id="V001",
                driver_id="D001",
                fuel_type="Regular",
                fuel_volume=Decimal(f"{10 + i}.0"),
                fuel_volume_unit="gallon",
                latitude=40.0 + (i/10),
                longitude=-74.0 - (i/10)
            )
            for i in range(1, 4)  # Create 3 transactions
        ]
        
        # Add a maintenance transaction
        transactions.append(
            MaintenanceTransaction(
                transaction_id="BATCH_M1",
                timestamp=now,
                amount=Decimal("150.00"),
                currency="USD",
                merchant_name="Batch Repair Shop",
                merchant_category="Maintenance",
                vehicle_id="V002",
                driver_id="D002",
                maintenance_type="Oil Change",
                odometer_reading=30000,
                latitude=41.0,
                longitude=-75.0
            )
        )
        
        # Create them in a batch
        created = await mock_db.batch_create_transactions(transactions)
        
        # Verify correct number created
        assert len(created) == 4
        
        # Verify they all exist in storage
        for txn_id in ["BATCH_F1", "BATCH_F2", "BATCH_F3", "BATCH_M1"]:
            txn = await mock_db.get_transaction_by_id(txn_id)
            assert txn is not None
            
        # Verify types preserved
        maint_txn = await mock_db.get_transaction_by_id("BATCH_M1")
        assert isinstance(maint_txn, MaintenanceTransaction)


class TestEntityOperations:
    """Test generic entity operations across different types."""
    
    @pytest.mark.asyncio
    async def test_create_entity(self, mock_db):
        """Test creating entities through the generic interface."""
        # Create a vehicle
        vehicle = Vehicle(
            vehicle_id="GENERIC_V1",
            make="Audi",
            model="A4",
            year=2022,
            vehicle_type="Sedan",
            fuel_capacity=Decimal("15.3"),
            fuel_capacity_unit="gallon"
        )
        
        # Create a driver
        driver = Driver(
            driver_id="GENERIC_D1",
            name="Generic Driver",
            license_number="DL-GENERIC-1"
        )
        
        # Use the generic interface
        created_vehicle = await mock_db.create_entity(vehicle)
        created_driver = await mock_db.create_entity(driver)
        
        assert created_vehicle.vehicle_id == "GENERIC_V1"
        assert created_driver.driver_id == "GENERIC_D1"
        
        # Verify they exist
        assert await mock_db.get_entity_by_id(Vehicle, "GENERIC_V1") is not None
        assert await mock_db.get_entity_by_id(Driver, "GENERIC_D1") is not None
    
    @pytest.mark.asyncio
    async def test_get_entity_by_id(self, mock_db):
        """Test retrieving entities by ID through the generic interface."""
        # Create entities first
        vehicle = Vehicle(
            vehicle_id="GET_ENTITY_V1",
            make="BMW",
            model="X5",
            year=2021,
            vehicle_type="SUV",
            fuel_capacity=Decimal("18.5"),
            fuel_capacity_unit="gallon"
        )
        await mock_db.create_vehicle(vehicle)
        
        # Test retrieving with different ID formats
        retrieved1 = await mock_db.get_entity_by_id(Vehicle, "GET_ENTITY_V1")
        retrieved2 = await mock_db.get_entity_by_id(Vehicle, "GET_ENTITY_V1")  # String ID
        
        assert retrieved1 is not None
        assert retrieved1.vehicle_id == "GET_ENTITY_V1"
        assert retrieved2 is not None
    
    @pytest.mark.asyncio
    async def test_update_entity(self, mock_db):
        """Test updating entities through the generic interface."""
        # Create a vehicle
        vehicle = Vehicle(
            vehicle_id="UPDATE_ENTITY_V1",
            make="Volvo",
            model="XC90",
            year=2020,
            vehicle_type="SUV",
            fuel_capacity=Decimal("19.2"),
            fuel_capacity_unit="gallon"
        )
        await mock_db.create_vehicle(vehicle)
        
        # Update it
        updated_vehicle = Vehicle(
            vehicle_id="UPDATE_ENTITY_V1",
            make="Volvo",
            model="XC90",
            year=2023,  # Updated year
            vehicle_type="SUV",
            fuel_capacity=Decimal("19.2"),
            fuel_capacity_unit="gallon"
        )
        
        # Use the generic interface
        result = await mock_db.update_entity(updated_vehicle)
        assert result.year == 2023
        
        # Verify update in storage
        saved = await mock_db.get_vehicle_by_id("UPDATE_ENTITY_V1")
        assert saved.year == 2023
    
    @pytest.mark.asyncio
    async def test_delete_entity(self, mock_db):
        """Test deleting entities through the generic interface."""
        # Create a vehicle
        vehicle = Vehicle(
            vehicle_id="DELETE_ENTITY_V1",
            make="Mazda",
            model="CX-5",
            year=2022,
            vehicle_type="SUV",
            fuel_capacity=Decimal("14.8"),
            fuel_capacity_unit="gallon"
        )
        await mock_db.create_vehicle(vehicle)
        
        # Delete it using the generic interface
        result = await mock_db.delete_entity(Vehicle, "DELETE_ENTITY_V1")
        assert result is True
        
        # Verify it's gone
        assert await mock_db.get_vehicle_by_id("DELETE_ENTITY_V1") is None


class TestErrorCases:
    """Test error handling and validation in MockDB."""
    
    @pytest.mark.asyncio
    async def test_duplicate_vehicle_id(self, mock_db):
        """Test that creating a vehicle with a duplicate ID raises an error."""
        # Create initial vehicle
        vehicle = Vehicle(
            vehicle_id="DUPLICATE_V1",
            make="Kia",
            model="Sorento",
            year=2021,
            vehicle_type="SUV",
            fuel_capacity=Decimal("16.2"),
            fuel_capacity_unit="gallon"
        )
        await mock_db.create_vehicle(vehicle)
        
        # Try to create another with same ID
        duplicate = Vehicle(
            vehicle_id="DUPLICATE_V1",  # Same ID
            make="Hyundai",
            model="Santa Fe",
            year=2022,
            vehicle_type="SUV",
            fuel_capacity=Decimal("17.4"),
            fuel_capacity_unit="gallon"
        )
        
        with pytest.raises(ValueError) as excinfo:
            await mock_db.create_vehicle(duplicate)
        
        assert "already exists" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_invalid_vehicle_reference(self, mock_db):
        """Test validation of vehicle references."""
        # Try to create a transaction with non-existent vehicle
        txn = FuelTransaction(
            transaction_id="INVALID_VEHICLE_TXN",
            timestamp=datetime.now(),
            amount=Decimal("45.00"),
            currency="USD",
            merchant_name="Test Station",
            merchant_category="Fuel",
            vehicle_id="NONEXISTENT_VEHICLE",  # This vehicle doesn't exist
            driver_id="D001",  # Valid driver from test data
            fuel_type="Regular",
            fuel_volume=Decimal("10.0"),
            fuel_volume_unit="gallon",
            latitude=40.0,
            longitude=-74.0
        )
        
        with pytest.raises(ValueError) as excinfo:
            await mock_db.create_transaction(txn)
        
        assert "does not exist" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_transaction_delete_protection(self, mock_db):
        """Test that vehicles with transactions cannot be deleted."""
        # Get vehicle with transactions
        vehicle_id = "V001"  # This vehicle has transactions in test data
        
        # Attempt to delete should fail
        with pytest.raises(ValueError) as excinfo:
            await mock_db.delete_vehicle(vehicle_id)
        
        assert "associated transactions" in str(excinfo.value)
    
    @pytest.mark.asyncio
    async def test_invalid_vehicle_assignment(self, mock_db):
        """Test validation of vehicle assignments for drivers."""
        # Try to create a driver with non-existent vehicle assignment
        driver = Driver(
            driver_id="INVALID_ASSIGNMENT_D1",
            name="Invalid Assignment Driver",
            assigned_vehicle_ids=["NONEXISTENT_VEHICLE"]  # This vehicle doesn't exist
        )
        
        with pytest.raises(ValueError) as excinfo:
            await mock_db.create_driver(driver)
        
        assert "non-existent vehicle" in str(excinfo.value) 