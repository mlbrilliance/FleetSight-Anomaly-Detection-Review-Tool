"""
Tests for the vehicle service.
"""

import pytest
from datetime import datetime, timedelta

from backend.models.vehicle import VehicleCreate, VehicleUpdate
from backend.services.vehicle_service import VehicleService


@pytest.mark.asyncio
async def test_get_vehicles(mock_supabase):
    """Test getting all vehicles."""
    service = VehicleService()
    vehicles = await service.get_vehicles()
    
    assert len(vehicles) == 1
    assert vehicles[0].make == "Toyota"
    assert vehicles[0].model == "Camry"
    assert vehicles[0].license_plate == "ABC123"
    assert vehicles[0].status == "active"


@pytest.mark.asyncio
async def test_get_vehicle(mock_supabase):
    """Test getting a specific vehicle."""
    service = VehicleService()
    vehicle_id = "123e4567-e89b-12d3-a456-426614174001"
    
    vehicle = await service.get_vehicle(vehicle_id)
    
    assert vehicle is not None
    assert vehicle.id == vehicle_id
    assert vehicle.make == "Toyota"
    assert vehicle.model == "Camry"
    assert vehicle.year == 2022
    assert vehicle.vin == "4T1BF1FK5CU123456"
    
    # Test getting a nonexistent vehicle
    vehicle = await service.get_vehicle("non-existent-id")
    assert vehicle is None


@pytest.mark.asyncio
async def test_create_vehicle(mock_supabase):
    """Test creating a new vehicle."""
    service = VehicleService()
    
    next_service_date = datetime.now() + timedelta(days=90)
    registration_expiry = datetime.now() + timedelta(days=365)
    insurance_expiry = datetime.now() + timedelta(days=180)
    
    new_vehicle = VehicleCreate(
        fleet_id="123e4567-e89b-12d3-a456-426614174002",
        make="Honda",
        model="Accord",
        year=2023,
        vin="1HGCV3F43MA001234",
        license_plate="XYZ789",
        status="active",
        color="Blue",
        fuel_type="Hybrid",
        purchase_date=datetime.fromisoformat("2023-01-10T00:00:00+00:00"),
        purchase_price=28000.00,
        mileage=5000,
        last_service_date=datetime.fromisoformat("2023-04-15T00:00:00+00:00"),
        next_service_date=next_service_date,
        registration_expiry=registration_expiry,
        insurance_expiry=insurance_expiry,
        notes="New fleet vehicle"
    )
    
    created_vehicle = await service.create_vehicle(new_vehicle)
    
    assert created_vehicle is not None
    assert created_vehicle.fleet_id == "123e4567-e89b-12d3-a456-426614174002"
    assert created_vehicle.make == "Honda"
    assert created_vehicle.model == "Accord"
    assert created_vehicle.license_plate == "XYZ789"
    assert created_vehicle.status == "active"
    
    # Check if the vehicle was added to the database
    all_vehicles = await service.get_vehicles()
    assert len(all_vehicles) == 2


@pytest.mark.asyncio
async def test_update_vehicle(mock_supabase):
    """Test updating a vehicle."""
    service = VehicleService()
    vehicle_id = "123e4567-e89b-12d3-a456-426614174001"
    
    update_data = VehicleUpdate(
        status="maintenance",
        mileage=15500,
        last_service_date=datetime.now(),
        notes="Vehicle in maintenance for brake service"
    )
    
    updated_vehicle = await service.update_vehicle(vehicle_id, update_data)
    
    assert updated_vehicle is not None
    assert updated_vehicle.id == vehicle_id
    assert updated_vehicle.status == "maintenance"
    assert updated_vehicle.mileage == 15500
    
    # Test updating nonexistent vehicle
    updated_vehicle = await service.update_vehicle("non-existent-id", update_data)
    assert updated_vehicle is None


@pytest.mark.asyncio
async def test_delete_vehicle(mock_supabase):
    """Test deleting a vehicle."""
    service = VehicleService()
    vehicle_id = "123e4567-e89b-12d3-a456-426614174001"
    
    # Verify the vehicle exists before deletion
    vehicle_before = await service.get_vehicle(vehicle_id)
    assert vehicle_before is not None
    
    # Delete the vehicle
    result = await service.delete_vehicle(vehicle_id)
    assert result is True
    
    # Verify the vehicle no longer exists
    vehicle_after = await service.get_vehicle(vehicle_id)
    assert vehicle_after is None
    
    # Test deleting nonexistent vehicle
    result = await service.delete_vehicle("non-existent-id")
    assert result is False


@pytest.mark.asyncio
async def test_get_vehicles_by_fleet(mock_supabase):
    """Test getting vehicles by fleet ID."""
    service = VehicleService()
    fleet_id = "123e4567-e89b-12d3-a456-426614174002"
    
    vehicles = await service.get_vehicles_by_fleet(fleet_id)
    
    assert len(vehicles) == 1
    assert vehicles[0].fleet_id == fleet_id
    assert vehicles[0].make == "Toyota"
    assert vehicles[0].model == "Camry"
    
    # Test with nonexistent fleet ID
    vehicles = await service.get_vehicles_by_fleet("non-existent-fleet")
    assert len(vehicles) == 0


@pytest.mark.asyncio
async def test_get_vehicles_by_status(mock_supabase):
    """Test getting vehicles by status."""
    service = VehicleService()
    
    # Test with active status
    vehicles = await service.get_vehicles_by_status("active")
    assert len(vehicles) == 1
    assert vehicles[0].status == "active"
    
    # Test with maintenance status
    vehicles = await service.get_vehicles_by_status("maintenance")
    assert len(vehicles) == 0
    
    # Update a vehicle to maintenance status
    vehicle_id = "123e4567-e89b-12d3-a456-426614174001"
    update_data = VehicleUpdate(status="maintenance")
    await service.update_vehicle(vehicle_id, update_data)
    
    # Check again with maintenance status
    vehicles = await service.get_vehicles_by_status("maintenance")
    assert len(vehicles) == 1
    assert vehicles[0].status == "maintenance"


@pytest.mark.asyncio
async def test_get_vehicle_stats(mock_supabase):
    """Test getting vehicle statistics."""
    service = VehicleService()
    vehicle_id = "123e4567-e89b-12d3-a456-426614174001"
    
    stats = await service.get_vehicle_stats(vehicle_id)
    
    assert stats is not None
    assert stats.get("total_trips") == 35
    assert stats.get("total_distance") == 1800
    assert stats.get("fuel_consumed") == 150
    assert stats.get("average_mpg") == 12.0
    assert stats.get("maintenance_cost") == 850
    assert stats.get("downtime_days") == 5
    assert stats.get("utilization_rate") == 85.0
    
    # Test with nonexistent vehicle ID
    stats = await service.get_vehicle_stats("non-existent-vehicle")
    assert stats is not None  # The mock returns default stats
    assert "total_trips" in stats
    assert "total_distance" in stats


@pytest.mark.asyncio
async def test_get_maintenance_alerts(mock_supabase):
    """Test getting maintenance alerts."""
    service = VehicleService()
    
    # Add a vehicle with service due soon
    next_service_date = datetime.now() + timedelta(days=5)
    new_vehicle = VehicleCreate(
        fleet_id="123e4567-e89b-12d3-a456-426614174002",
        make="Ford",
        model="F-150",
        year=2021,
        vin="1FTEX1EP5MKE12345",
        license_plate="MNO456",
        status="active",
        mileage=25000,
        next_service_date=next_service_date
    )
    
    await service.create_vehicle(new_vehicle)
    
    # Get vehicles with maintenance due in 7 days
    vehicles = await service.get_maintenance_alerts(days=7)
    
    assert len(vehicles) == 1
    assert vehicles[0].make == "Ford"
    assert vehicles[0].model == "F-150"
    
    # Get vehicles with maintenance due in 3 days (should return none)
    vehicles = await service.get_maintenance_alerts(days=3)
    assert len(vehicles) == 0


@pytest.mark.asyncio
async def test_get_registration_expiry_alerts(mock_supabase):
    """Test getting registration expiry alerts."""
    service = VehicleService()
    
    # Add a vehicle with registration expiring soon
    registration_expiry = datetime.now() + timedelta(days=15)
    new_vehicle = VehicleCreate(
        fleet_id="123e4567-e89b-12d3-a456-426614174002",
        make="Chevrolet",
        model="Malibu",
        year=2022,
        vin="1G1ZD5ST8NF123456",
        license_plate="PQR789",
        status="active",
        registration_expiry=registration_expiry
    )
    
    await service.create_vehicle(new_vehicle)
    
    # Get vehicles with registration expiring in 30 days
    vehicles = await service.get_registration_expiry_alerts(days=30)
    
    assert len(vehicles) == 1
    assert vehicles[0].make == "Chevrolet"
    assert vehicles[0].model == "Malibu"
    
    # Get vehicles with registration expiring in 10 days (should return none)
    vehicles = await service.get_registration_expiry_alerts(days=10)
    assert len(vehicles) == 0


@pytest.mark.asyncio
async def test_get_insurance_expiry_alerts(mock_supabase):
    """Test getting insurance expiry alerts."""
    service = VehicleService()
    
    # Add a vehicle with insurance expiring soon
    insurance_expiry = datetime.now() + timedelta(days=25)
    new_vehicle = VehicleCreate(
        fleet_id="123e4567-e89b-12d3-a456-426614174002",
        make="Nissan",
        model="Altima",
        year=2021,
        vin="1N4BL4EV1NN123456",
        license_plate="STU012",
        status="active",
        insurance_expiry=insurance_expiry
    )
    
    await service.create_vehicle(new_vehicle)
    
    # Get vehicles with insurance expiring in 30 days
    vehicles = await service.get_insurance_expiry_alerts(days=30)
    
    assert len(vehicles) == 1
    assert vehicles[0].make == "Nissan"
    assert vehicles[0].model == "Altima"
    
    # Get vehicles with insurance expiring in 20 days (should return none)
    vehicles = await service.get_insurance_expiry_alerts(days=20)
    assert len(vehicles) == 0 