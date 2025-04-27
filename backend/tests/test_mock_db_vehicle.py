"""
Tests for the MockDB Vehicle Repository implementation.
[OWL: fleetsight-system.ttl#TestSuite]

This module tests the MockDB implementation of the VehicleRepository interface.
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