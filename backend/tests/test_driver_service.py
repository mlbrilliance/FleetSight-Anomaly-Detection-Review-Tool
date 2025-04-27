"""
Tests for the driver service.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from backend.models.driver import Driver, DriverCreate, DriverUpdate
from backend.services.driver_service import DriverService


@pytest.mark.asyncio
async def test_get_all_drivers(mock_supabase):
    """Test getting all drivers."""
    # Arrange
    driver_service = DriverService()
    
    # Act
    drivers = await driver_service.get_all_drivers()
    
    # Assert
    assert len(drivers) == 1
    assert drivers[0].id == "123e4567-e89b-12d3-a456-426614174000"
    assert drivers[0].first_name == "John"
    assert drivers[0].last_name == "Doe"
    assert drivers[0].email == "john.doe@example.com"


@pytest.mark.asyncio
async def test_get_driver_by_id(mock_supabase):
    """Test getting a driver by ID."""
    # Arrange
    driver_service = DriverService()
    driver_id = "123e4567-e89b-12d3-a456-426614174000"
    
    # Act
    driver = await driver_service.get_driver_by_id(driver_id)
    
    # Assert
    assert driver is not None
    assert driver.id == driver_id
    assert driver.first_name == "John"
    assert driver.last_name == "Doe"
    assert driver.email == "john.doe@example.com"


@pytest.mark.asyncio
async def test_get_driver_by_id_not_found(mock_supabase):
    """Test getting a driver by ID when the driver doesn't exist."""
    # Arrange
    driver_service = DriverService()
    driver_id = "non-existent-id"
    
    # Configure the mock to return empty data for this ID
    with patch('backend.db.supabase_client.get_supabase_client') as mock_get_client:
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_table.select.return_value.__aenter__.return_value = MagicMock(data=[])
        mock_client.table.return_value = mock_table
        mock_get_client.return_value = mock_client
        
        # Act/Assert
        with pytest.raises(ValueError, match="Driver not found"):
            await driver_service.get_driver_by_id(driver_id)


@pytest.mark.asyncio
async def test_create_driver(mock_supabase):
    """Test creating a driver."""
    # Arrange
    driver_service = DriverService()
    driver_create = DriverCreate(
        fleet_id="123e4567-e89b-12d3-a456-426614174002",
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        phone="555-987-6543",
        license_number="DL98765432",
        license_expiry=datetime.now() + timedelta(days=365),
        date_of_birth=datetime.strptime("1990-10-20", "%Y-%m-%d").date(),
        date_hired=datetime.strptime("2022-05-15", "%Y-%m-%d").date(),
        status="active",
        address="456 Park Ave, Anytown, USA",
        emergency_contact_name="John Smith",
        emergency_contact_phone="555-123-4567",
        next_review_date=datetime.now() + timedelta(days=90),
        notes="New driver with excellent credentials"
    )
    
    # Act
    new_driver = await driver_service.create_driver(driver_create)
    
    # Assert
    assert new_driver is not None
    assert new_driver.id is not None
    assert new_driver.first_name == "Jane"
    assert new_driver.last_name == "Smith"
    assert new_driver.email == "jane.smith@example.com"
    assert new_driver.fleet_id == "123e4567-e89b-12d3-a456-426614174002"


@pytest.mark.asyncio
async def test_update_driver(mock_supabase):
    """Test updating a driver."""
    # Arrange
    driver_service = DriverService()
    driver_id = "123e4567-e89b-12d3-a456-426614174000"
    driver_update = DriverUpdate(
        first_name="John",
        last_name="Doe",
        email="john.updated@example.com",
        phone="555-111-2222",
        status="inactive",
        notes="Updated driver information"
    )
    
    # Act
    updated_driver = await driver_service.update_driver(driver_id, driver_update)
    
    # Assert
    assert updated_driver is not None
    assert updated_driver.id == driver_id
    assert updated_driver.email == "john.updated@example.com"
    assert updated_driver.phone == "555-111-2222"
    assert updated_driver.status == "inactive"
    assert updated_driver.notes == "Updated driver information"


@pytest.mark.asyncio
async def test_delete_driver(mock_supabase):
    """Test deleting a driver."""
    # Arrange
    driver_service = DriverService()
    driver_id = "123e4567-e89b-12d3-a456-426614174000"
    
    # Act
    result = await driver_service.delete_driver(driver_id)
    
    # Assert
    assert result is True


@pytest.mark.asyncio
async def test_get_drivers_by_fleet(mock_supabase):
    """Test getting drivers by fleet ID."""
    # Arrange
    driver_service = DriverService()
    fleet_id = "123e4567-e89b-12d3-a456-426614174002"
    
    # Act
    drivers = await driver_service.get_drivers_by_fleet(fleet_id)
    
    # Assert
    assert len(drivers) == 1
    assert drivers[0].id == "123e4567-e89b-12d3-a456-426614174000"
    assert drivers[0].fleet_id == fleet_id


@pytest.mark.asyncio
async def test_get_driver_stats(mock_supabase):
    """Test getting driver statistics."""
    # Arrange
    driver_service = DriverService()
    driver_id = "123e4567-e89b-12d3-a456-426614174000"
    
    # Act
    stats = await driver_service.get_driver_stats(driver_id)
    
    # Assert
    assert stats is not None
    assert stats.total_trips == 25
    assert stats.total_distance == 1200
    assert stats.active_days == 20
    assert stats.violations == 0
    assert stats.incidents == 0
    assert stats.fuel_consumption == 120
    assert stats.efficiency_score == 92.5


@pytest.mark.asyncio
async def test_get_driver_stats_not_found(mock_supabase):
    """Test getting stats for a driver that doesn't exist."""
    # Arrange
    driver_service = DriverService()
    driver_id = "non-existent-id"
    
    # Act
    stats = await driver_service.get_driver_stats(driver_id)
    
    # Assert
    assert stats is not None
    assert stats.total_trips == 0
    assert stats.total_distance == 0
    assert stats.active_days == 0
    assert stats.violations == 0
    assert stats.incidents == 0
    assert stats.fuel_consumption == 0
    assert stats.efficiency_score == 0.0 