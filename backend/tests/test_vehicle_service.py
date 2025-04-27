"""
Tests for the vehicle service.
"""

import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from backend.models.vehicle import Vehicle, VehicleCreate, VehicleUpdate
from backend.services.vehicle_service import VehicleService


@pytest.mark.asyncio
async def test_get_all_vehicles(mock_supabase):
    """Test getting all vehicles."""
    # Arrange
    vehicle_service = VehicleService()
    
    # Act
    vehicles = await vehicle_service.get_all_vehicles()
    
    # Assert
    assert len(vehicles) == 1
    assert vehicles[0].id == "123e4567-e89b-12d3-a456-426614174001"
    assert vehicles[0].make == "Toyota"
    assert vehicles[0].model == "Camry"
    assert vehicles[0].year == 2022
    assert vehicles[0].vin == "4T1BF1FK5CU123456"


@pytest.mark.asyncio
async def test_get_vehicle_by_id(mock_supabase):
    """Test getting a vehicle by ID."""
    # Arrange
    vehicle_service = VehicleService()
    vehicle_id = "123e4567-e89b-12d3-a456-426614174001"
    
    # Act
    vehicle = await vehicle_service.get_vehicle_by_id(vehicle_id)
    
    # Assert
    assert vehicle is not None
    assert vehicle.id == vehicle_id
    assert vehicle.make == "Toyota"
    assert vehicle.model == "Camry"
    assert vehicle.year == 2022
    assert vehicle.vin == "4T1BF1FK5CU123456"


@pytest.mark.asyncio
async def test_get_vehicle_by_id_not_found(mock_supabase):
    """Test getting a vehicle by ID when the vehicle doesn't exist."""
    # Arrange
    vehicle_service = VehicleService()
    vehicle_id = "non-existent-id"
    
    # Configure the mock to return empty data for this ID
    with patch('backend.db.supabase_client.get_supabase_client') as mock_get_client:
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_table.select.return_value.__aenter__.return_value = MagicMock(data=[])
        mock_client.table.return_value = mock_table
        mock_get_client.return_value = mock_client
        
        # Act/Assert
        with pytest.raises(ValueError, match="Vehicle not found"):
            await vehicle_service.get_vehicle_by_id(vehicle_id)


@pytest.mark.asyncio
async def test_create_vehicle(mock_supabase):
    """Test creating a vehicle."""
    # Arrange
    vehicle_service = VehicleService()
    vehicle_create = VehicleCreate(
        fleet_id="123e4567-e89b-12d3-a456-426614174002",
        make="Honda",
        model="Accord",
        year=2023,
        vin="1HGCV2F34NA123456",
        license_plate="XYZ789",
        status="active",
        color="Black",
        fuel_type="Gasoline",
        purchase_date=datetime.strptime("2023-01-15", "%Y-%m-%d").date(),
        purchase_price=28000.00,
        mileage=5000,
        last_service_date=datetime.strptime("2023-05-10", "%Y-%m-%d").date(),
        next_service_date=datetime.now() + timedelta(days=90),
        registration_expiry=datetime.now() + timedelta(days=365),
        insurance_expiry=datetime.now() + timedelta(days=180),
        notes="New executive vehicle"
    )
    
    # Act
    new_vehicle = await vehicle_service.create_vehicle(vehicle_create)
    
    # Assert
    assert new_vehicle is not None
    assert new_vehicle.id is not None
    assert new_vehicle.make == "Honda"
    assert new_vehicle.model == "Accord"
    assert new_vehicle.year == 2023
    assert new_vehicle.vin == "1HGCV2F34NA123456"
    assert new_vehicle.fleet_id == "123e4567-e89b-12d3-a456-426614174002"


@pytest.mark.asyncio
async def test_update_vehicle(mock_supabase):
    """Test updating a vehicle."""
    # Arrange
    vehicle_service = VehicleService()
    vehicle_id = "123e4567-e89b-12d3-a456-426614174001"
    vehicle_update = VehicleUpdate(
        mileage=20000,
        status="maintenance",
        last_service_date=datetime.now().date(),
        next_service_date=(datetime.now() + timedelta(days=180)).date(),
        notes="Updated after regular maintenance"
    )
    
    # Act
    updated_vehicle = await vehicle_service.update_vehicle(vehicle_id, vehicle_update)
    
    # Assert
    assert updated_vehicle is not None
    assert updated_vehicle.id == vehicle_id
    assert updated_vehicle.mileage == 20000
    assert updated_vehicle.status == "maintenance"
    assert updated_vehicle.notes == "Updated after regular maintenance"


@pytest.mark.asyncio
async def test_delete_vehicle(mock_supabase):
    """Test deleting a vehicle."""
    # Arrange
    vehicle_service = VehicleService()
    vehicle_id = "123e4567-e89b-12d3-a456-426614174001"
    
    # Act
    result = await vehicle_service.delete_vehicle(vehicle_id)
    
    # Assert
    assert result is True


@pytest.mark.asyncio
async def test_get_vehicles_by_fleet(mock_supabase):
    """Test getting vehicles by fleet ID."""
    # Arrange
    vehicle_service = VehicleService()
    fleet_id = "123e4567-e89b-12d3-a456-426614174002"
    
    # Act
    vehicles = await vehicle_service.get_vehicles_by_fleet(fleet_id)
    
    # Assert
    assert len(vehicles) == 1
    assert vehicles[0].id == "123e4567-e89b-12d3-a456-426614174001"
    assert vehicles[0].fleet_id == fleet_id


@pytest.mark.asyncio
async def test_get_vehicle_stats(mock_supabase):
    """Test getting vehicle statistics."""
    # Arrange
    vehicle_service = VehicleService()
    vehicle_id = "123e4567-e89b-12d3-a456-426614174001"
    
    # Act
    stats = await vehicle_service.get_vehicle_stats(vehicle_id)
    
    # Assert
    assert stats is not None
    assert stats.total_trips == 35
    assert stats.total_distance == 1800
    assert stats.fuel_consumed == 150
    assert stats.average_mpg == 12.0
    assert stats.maintenance_cost == 850
    assert stats.downtime_days == 5
    assert stats.utilization_rate == 85.0


@pytest.mark.asyncio
async def test_get_vehicle_stats_not_found(mock_supabase):
    """Test getting stats for a vehicle that doesn't exist."""
    # Arrange
    vehicle_service = VehicleService()
    vehicle_id = "non-existent-id"
    
    # Act
    stats = await vehicle_service.get_vehicle_stats(vehicle_id)
    
    # Assert
    assert stats is not None
    assert stats.total_trips == 0
    assert stats.total_distance == 0
    assert stats.fuel_consumed == 0
    assert stats.average_mpg == 0.0
    assert stats.maintenance_cost == 0
    assert stats.downtime_days == 0
    assert stats.utilization_rate == 0.0 