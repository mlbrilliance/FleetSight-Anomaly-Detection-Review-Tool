"""
Tests for vehicle API endpoints.

This module contains tests for the vehicle API endpoints.
"""

import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from datetime import datetime

from backend.main import app
from backend.models.vehicle import Vehicle, VehicleStatus, VehicleType


# Sample vehicle data for testing
SAMPLE_VEHICLE = {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "make": "Toyota",
    "model": "Camry",
    "year": 2020,
    "license_plate": "ABC123",
    "vin": "1HGBH41JXMN109186",
    "status": VehicleStatus.ACTIVE,
    "vehicle_type": VehicleType.CAR,
    "mileage": 15000,
    "fuel_type": "Gasoline",
    "color": "Blue",
    "notes": "Company car",
    "created_at": datetime.now(),
    "updated_at": datetime.now()
}


@pytest.fixture
def vehicle_data():
    """Fixture to provide sample vehicle data."""
    return {
        "make": "Toyota",
        "model": "Camry",
        "year": 2020,
        "license_plate": "ABC123",
        "vin": "1HGBH41JXMN109186",
        "status": "active",
        "vehicle_type": "car",
        "mileage": 15000,
        "fuel_type": "Gasoline",
        "color": "Blue",
        "notes": "Company car"
    }


@pytest.mark.asyncio
@patch("backend.services.fleet_service.get_vehicles")
async def test_read_vehicles(mock_get_vehicles, vehicle_data):
    """Test the read_vehicles endpoint."""
    # Set up the mock
    vehicle = Vehicle(
        id="123e4567-e89b-12d3-a456-426614174000",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        **vehicle_data
    )
    mock_get_vehicles.return_value = [vehicle]
    
    # Make request to the endpoint
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/vehicles")
    
    # Assertions
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == vehicle.id


@pytest.mark.asyncio
@patch("backend.services.fleet_service.get_vehicle_by_id")
async def test_read_vehicle(mock_get_vehicle_by_id, vehicle_data):
    """Test the read_vehicle endpoint."""
    # Set up the mock
    vehicle_id = "123e4567-e89b-12d3-a456-426614174000"
    vehicle = Vehicle(
        id=vehicle_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        **vehicle_data
    )
    mock_get_vehicle_by_id.return_value = vehicle
    
    # Make request to the endpoint
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/vehicles/{vehicle_id}")
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["id"] == vehicle_id


@pytest.mark.asyncio
@patch("backend.services.fleet_service.get_vehicle_by_id")
async def test_read_vehicle_not_found(mock_get_vehicle_by_id):
    """Test the read_vehicle endpoint when vehicle not found."""
    # Set up the mock
    vehicle_id = "nonexistent-id"
    mock_get_vehicle_by_id.return_value = None
    
    # Make request to the endpoint
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/vehicles/{vehicle_id}")
    
    # Assertions
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
@patch("backend.services.fleet_service.create_vehicle")
async def test_create_vehicle(mock_create_vehicle, vehicle_data):
    """Test the create_vehicle endpoint."""
    # Set up the mock
    vehicle = Vehicle(
        id="123e4567-e89b-12d3-a456-426614174000",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        **vehicle_data
    )
    mock_create_vehicle.return_value = vehicle
    
    # Make request to the endpoint
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/vehicles", json=vehicle_data)
    
    # Assertions
    assert response.status_code == 201
    assert response.json()["id"] == vehicle.id


@pytest.mark.asyncio
@patch("backend.services.fleet_service.update_vehicle")
async def test_update_vehicle(mock_update_vehicle, vehicle_data):
    """Test the update_vehicle endpoint."""
    # Set up the mock
    vehicle_id = "123e4567-e89b-12d3-a456-426614174000"
    update_data = {"mileage": 20000, "notes": "Updated notes"}
    
    updated_vehicle = Vehicle(
        id=vehicle_id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        **{**vehicle_data, **update_data}
    )
    
    mock_update_vehicle.return_value = updated_vehicle
    
    # Make request to the endpoint
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(f"/vehicles/{vehicle_id}", json=update_data)
    
    # Assertions
    assert response.status_code == 200
    assert response.json()["id"] == vehicle_id
    assert response.json()["mileage"] == update_data["mileage"]
    assert response.json()["notes"] == update_data["notes"]


@pytest.mark.asyncio
@patch("backend.services.fleet_service.update_vehicle")
async def test_update_vehicle_not_found(mock_update_vehicle):
    """Test the update_vehicle endpoint when vehicle not found."""
    # Set up the mock
    vehicle_id = "nonexistent-id"
    update_data = {"mileage": 20000}
    mock_update_vehicle.return_value = None
    
    # Make request to the endpoint
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.put(f"/vehicles/{vehicle_id}", json=update_data)
    
    # Assertions
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
@patch("backend.services.fleet_service.delete_vehicle")
async def test_delete_vehicle(mock_delete_vehicle):
    """Test the delete_vehicle endpoint."""
    # Set up the mock
    vehicle_id = "123e4567-e89b-12d3-a456-426614174000"
    mock_delete_vehicle.return_value = True
    
    # Make request to the endpoint
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(f"/vehicles/{vehicle_id}")
    
    # Assertions
    assert response.status_code == 204
    assert response.content == b''


@pytest.mark.asyncio
@patch("backend.services.fleet_service.delete_vehicle")
async def test_delete_vehicle_not_found(mock_delete_vehicle):
    """Test the delete_vehicle endpoint when vehicle not found."""
    # Set up the mock
    vehicle_id = "nonexistent-id"
    mock_delete_vehicle.return_value = False
    
    # Make request to the endpoint
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete(f"/vehicles/{vehicle_id}")
    
    # Assertions
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower() 