"""
Tests for the MockDB Driver Repository implementation.
[OWL: fleetsight-system.ttl#TestSuite]

This module tests the MockDB implementation of the DriverRepository interface.
"""
import pytest
import pytest_asyncio
from datetime import date

from shared_models.models import Driver, Vehicle
from backend.db.mock_db import MockDB
from decimal import Decimal

@pytest_asyncio.fixture
async def mock_db():
    """Create and initialize a MockDB instance for testing."""
    db = MockDB()
    await db.connect()
    yield db
    await db.disconnect()


class TestDriverRepository:
    """Test MockDB's DriverRepository implementation."""
    
    @pytest.mark.asyncio
    async def test_create_driver(self, mock_db):
        """Test driver creation."""
        new_driver = Driver(
            driver_id="TEST_D1",
            name="John Doe",
            license_number="DL123456",
            assigned_vehicle_ids=[]
        )
        
        created = await mock_db.create_driver(new_driver)
        assert created.driver_id == "TEST_D1"
        assert created.name == "John Doe"
        
        # Verify created in storage
        saved = await mock_db.get_driver_by_id("TEST_D1")
        assert saved is not None
        assert saved.name == "John Doe"
        assert saved.license_number == "DL123456"
    
    @pytest.mark.asyncio
    async def test_update_driver(self, mock_db):
        """Test driver update."""
        # Create a driver first
        original = Driver(
            driver_id="UPDATE_D1",
            name="Jane Smith",
            license_number="DL654321",
            assigned_vehicle_ids=[]
        )
        await mock_db.create_driver(original)
        
        # Update it
        updated = Driver(
            driver_id="UPDATE_D1",
            name="Jane Johnson",
            license_number="DL654321",
            assigned_vehicle_ids=[]
        )
        result = await mock_db.update_driver(updated)
        
        # Verify updated
        assert result.name == "Jane Johnson"
        assert result.license_number == "DL654321"
        
        # Verify in storage
        saved = await mock_db.get_driver_by_id("UPDATE_D1")
        assert saved is not None
        assert saved.name == "Jane Johnson"
        assert saved.license_number == "DL654321"
    
    @pytest.mark.asyncio
    async def test_get_all_drivers(self, mock_db):
        """Test retrieval of all drivers with pagination."""
        # Create some test drivers
        for i in range(5):
            driver = Driver(
                driver_id=f"PAGINATE_D{i}",
                name=f"Test Driver {i}",
                license_number=f"DL{i}",
                assigned_vehicle_ids=[]
            )
            await mock_db.create_driver(driver)
        
        # Test pagination
        first_page = await mock_db.get_all_drivers(limit=3, offset=0)
        second_page = await mock_db.get_all_drivers(limit=3, offset=3)
        
        assert len(first_page) == 3
        assert len(second_page) >= 2  # Could be more depending on pre-existing data
        
        # Get all drivers to verify total count
        all_drivers = await mock_db.get_all_drivers()
        assert len(all_drivers) >= 5  # At least our 5 plus any pre-existing
    
    @pytest.mark.asyncio
    async def test_get_drivers_by_vehicle(self, mock_db):
        """Test retrieving drivers by assigned vehicle."""
        # Create test vehicles
        test_vehicle = Vehicle(
            vehicle_id="DRIVER_TEST_V1",
            make="Ford",
            model="F-150",
            year=2021,
            vehicle_type="Truck",
            fuel_capacity=Decimal("25.0"),
            fuel_capacity_unit="gallon"
        )
        await mock_db.create_vehicle(test_vehicle)
        
        # Create a second vehicle for the test
        other_vehicle = Vehicle(
            vehicle_id="OTHER_VEHICLE",
            make="Toyota",
            model="Camry",
            year=2020,
            vehicle_type="Sedan",
            fuel_capacity=Decimal("14.5"),
            fuel_capacity_unit="gallon"
        )
        await mock_db.create_vehicle(other_vehicle)
        
        # Create drivers with different vehicle assignments
        driver1 = Driver(
            driver_id="VEHICLE_D1",
            name="Vehicle Driver1",
            license_number="VDL1",
            assigned_vehicle_ids=["DRIVER_TEST_V1"]
        )
        await mock_db.create_driver(driver1)
        
        driver2 = Driver(
            driver_id="VEHICLE_D2",
            name="Vehicle Driver2",
            license_number="VDL2",
            assigned_vehicle_ids=["DRIVER_TEST_V1", "OTHER_VEHICLE"]
        )
        await mock_db.create_driver(driver2)
        
        driver3 = Driver(
            driver_id="VEHICLE_D3",
            name="Vehicle Driver3",
            license_number="VDL3",
            assigned_vehicle_ids=["OTHER_VEHICLE"]
        )
        await mock_db.create_driver(driver3)
        
        # Test get_drivers_by_vehicle
        drivers = await mock_db.get_drivers_by_vehicle("DRIVER_TEST_V1")
        
        # Should return driver1 and driver2 (assigned to DRIVER_TEST_V1)
        assert len(drivers) == 2
        driver_ids = [d.driver_id for d in drivers]
        assert "VEHICLE_D1" in driver_ids
        assert "VEHICLE_D2" in driver_ids
        assert "VEHICLE_D3" not in driver_ids
    
    @pytest.mark.asyncio
    async def test_delete_driver(self, mock_db):
        """Test driver deletion."""
        # Create a driver to delete
        delete_driver = Driver(
            driver_id="DELETE_D1",
            name="Delete Driver",
            license_number="DDL1",
            assigned_vehicle_ids=[]
        )
        await mock_db.create_driver(delete_driver)
        
        # Verify it exists
        assert await mock_db.get_driver_by_id("DELETE_D1") is not None
        
        # Delete it
        result = await mock_db.delete_driver("DELETE_D1")
        assert result is True
        
        # Verify it's gone
        assert await mock_db.get_driver_by_id("DELETE_D1") is None
        
        # Deleting non-existent should return False
        result = await mock_db.delete_driver("NONEXISTENT")
        assert result is False 