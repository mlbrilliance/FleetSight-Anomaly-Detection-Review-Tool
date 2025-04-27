"""
Tests for the driver service.
"""

import pytest
from uuid import uuid4
from datetime import date, datetime, timedelta

from backend.models.driver import DriverCreate, DriverUpdate
from backend.services.driver_service import DriverService


@pytest.mark.asyncio
async def test_get_drivers(mock_supabase):
    """Test getting all drivers."""
    service = DriverService()
    drivers = await service.get_drivers()
    
    assert len(drivers) == 1
    assert drivers[0].first_name == "John"
    assert drivers[0].last_name == "Doe"
    assert drivers[0].email == "john.doe@example.com"
    assert drivers[0].status == "active"


@pytest.mark.asyncio
async def test_get_driver(mock_supabase):
    """Test getting a specific driver."""
    service = DriverService()
    driver = await service.get_driver("123e4567-e89b-12d3-a456-426614174000")
    
    assert driver is not None
    assert driver.id == "123e4567-e89b-12d3-a456-426614174000"
    assert driver.first_name == "John"
    assert driver.last_name == "Doe"
    assert driver.email == "john.doe@example.com"
    assert driver.license_number == "DL12345678"
    
    # Test getting a nonexistent driver
    driver = await service.get_driver("non-existent-id")
    assert driver is None


@pytest.mark.asyncio
async def test_create_driver(mock_supabase):
    """Test creating a new driver."""
    service = DriverService()
    
    license_expiry = datetime.now() + timedelta(days=365)
    next_review_date = datetime.now() + timedelta(days=90)
    
    new_driver = DriverCreate(
        fleet_id="123e4567-e89b-12d3-a456-426614174002",
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        phone="555-987-6543",
        license_number="DL87654321",
        license_expiry=license_expiry,
        date_of_birth=datetime.fromisoformat("1990-08-20T00:00:00+00:00"),
        date_hired=datetime.fromisoformat("2022-02-15T00:00:00+00:00"),
        status="active",
        address="456 Oak Avenue, Anytown, USA",
        emergency_contact_name="John Smith",
        emergency_contact_phone="555-123-4567",
        next_review_date=next_review_date,
        notes="New driver with clean record"
    )
    
    created_driver = await service.create_driver(new_driver)
    
    assert created_driver is not None
    assert created_driver.fleet_id == "123e4567-e89b-12d3-a456-426614174002"
    assert created_driver.first_name == "Jane"
    assert created_driver.last_name == "Smith"
    assert created_driver.email == "jane.smith@example.com"
    assert created_driver.license_number == "DL87654321"
    
    # Check if the driver was added to the database
    all_drivers = await service.get_drivers()
    assert len(all_drivers) == 2


@pytest.mark.asyncio
async def test_update_driver(mock_supabase):
    """Test updating a driver."""
    service = DriverService()
    driver_id = "123e4567-e89b-12d3-a456-426614174000"
    
    update_data = DriverUpdate(
        email="john.doe.updated@example.com",
        phone="555-555-5555",
        status="inactive",
        notes="Driver temporarily inactive"
    )
    
    updated_driver = await service.update_driver(driver_id, update_data)
    
    assert updated_driver is not None
    assert updated_driver.id == driver_id
    assert updated_driver.email == "john.doe.updated@example.com"
    assert updated_driver.status == "inactive"
    
    # Check if the driver was updated in the database
    driver = await service.get_driver(driver_id)
    assert driver.email == "john.doe.updated@example.com"
    assert driver.status == "inactive"
    
    # Test updating nonexistent driver
    updated_driver = await service.update_driver("non-existent-id", update_data)
    assert updated_driver is None


@pytest.mark.asyncio
async def test_delete_driver(mock_supabase):
    """Test deleting a driver."""
    service = DriverService()
    driver_id = "123e4567-e89b-12d3-a456-426614174000"
    
    # Verify the driver exists before deletion
    driver_before = await service.get_driver(driver_id)
    assert driver_before is not None
    
    # Delete the driver
    result = await service.delete_driver(driver_id)
    assert result is True
    
    # Verify the driver no longer exists
    driver_after = await service.get_driver(driver_id)
    assert driver_after is None
    
    # Test deleting nonexistent driver
    result = await service.delete_driver("non-existent-id")
    assert result is False


@pytest.mark.asyncio
async def test_get_drivers_by_fleet(mock_supabase):
    """Test getting drivers by fleet ID."""
    service = DriverService()
    fleet_id = "123e4567-e89b-12d3-a456-426614174002"
    
    drivers = await service.get_drivers_by_fleet(fleet_id)
    
    assert len(drivers) == 1
    assert drivers[0].fleet_id == fleet_id
    assert drivers[0].first_name == "John"
    assert drivers[0].last_name == "Doe"
    
    # Test with nonexistent fleet ID
    drivers = await service.get_drivers_by_fleet("non-existent-fleet")
    assert len(drivers) == 0


@pytest.mark.asyncio
async def test_get_drivers_by_status(mock_supabase):
    """Test getting drivers by status."""
    service = DriverService()
    
    # Test with active status
    drivers = await service.get_drivers_by_status("active")
    assert len(drivers) == 1
    assert drivers[0].status == "active"
    
    # Test with inactive status
    drivers = await service.get_drivers_by_status("inactive")
    assert len(drivers) == 0
    
    # Update a driver to inactive status
    driver_id = "123e4567-e89b-12d3-a456-426614174000"
    update_data = DriverUpdate(status="inactive")
    await service.update_driver(driver_id, update_data)
    
    # Check again with inactive status
    drivers = await service.get_drivers_by_status("inactive")
    assert len(drivers) == 1
    assert drivers[0].status == "inactive"


@pytest.mark.asyncio
async def test_get_drivers_license_expiring_soon(mock_supabase):
    """Test getting drivers with licenses expiring soon."""
    service = DriverService()
    
    # Add a driver with a license expiring soon
    new_driver = DriverCreate(
        fleet_id="123e4567-e89b-12d3-a456-426614174002",
        first_name="Expiring",
        last_name="License",
        email="expiring.license@example.com",
        phone="555-111-2222",
        license_number="DL22222222",
        license_expiry=datetime.now().replace(microsecond=0) + datetime.timedelta(days=25),
        date_of_birth=datetime.fromisoformat("1988-03-15T00:00:00+00:00"),
        date_hired=datetime.fromisoformat("2022-01-10T00:00:00+00:00"),
        status="active"
    )
    
    await service.create_driver(new_driver)
    
    # Get drivers with licenses expiring in 30 days
    drivers = await service.get_drivers_license_expiring(days=30)
    
    assert len(drivers) == 1
    assert drivers[0].first_name == "Expiring"
    assert drivers[0].last_name == "License"
    
    # Get drivers with licenses expiring in 10 days (should return none)
    drivers = await service.get_drivers_license_expiring(days=10)
    assert len(drivers) == 0


@pytest.mark.asyncio
async def test_get_driver_stats(mock_supabase):
    """Test getting driver statistics."""
    service = DriverService()
    driver_id = "123e4567-e89b-12d3-a456-426614174000"
    
    stats = await service.get_driver_stats(driver_id)
    
    assert stats is not None
    assert stats.get("total_trips") == 25
    assert stats.get("total_distance") == 1200
    assert stats.get("active_days") == 20
    assert stats.get("violations") == 0
    assert stats.get("incidents") == 0
    assert stats.get("fuel_consumption") == 120
    assert stats.get("efficiency_score") == 92.5
    
    # Test with nonexistent driver ID
    stats = await service.get_driver_stats("non-existent-driver")
    assert stats is not None
    assert stats.get("total_trips") == 0
    assert stats.get("total_distance") == 0
    assert stats.get("active_days") == 0
    assert stats.get("violations") == 0
    assert stats.get("incidents") == 0
    assert stats.get("fuel_consumption") == 0
    assert stats.get("efficiency_score") == 0.0


@pytest.mark.asyncio
async def test_get_license_expiry_alerts(mock_supabase):
    """Test getting license expiry alerts."""
    service = DriverService()
    
    # Add a driver with license expiring soon
    license_expiry = datetime.now() + timedelta(days=20)
    new_driver = DriverCreate(
        fleet_id="123e4567-e89b-12d3-a456-426614174002",
        first_name="Robert",
        last_name="Johnson",
        email="robert.johnson@example.com",
        license_number="DL55555555",
        license_expiry=license_expiry,
        status="active"
    )
    
    await service.create_driver(new_driver)
    
    # Get drivers with licenses expiring in 30 days
    drivers = await service.get_license_expiry_alerts(days=30)
    
    assert len(drivers) == 1
    assert drivers[0].first_name == "Robert"
    assert drivers[0].last_name == "Johnson"
    
    # Get drivers with licenses expiring in 10 days (should return none)
    drivers = await service.get_license_expiry_alerts(days=10)
    assert len(drivers) == 0 