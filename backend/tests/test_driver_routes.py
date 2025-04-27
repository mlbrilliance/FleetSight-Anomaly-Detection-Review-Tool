"""
Integration tests for the driver API routes.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from backend.models.driver import DriverCreate, DriverUpdate


def test_get_all_drivers(test_app, mock_supabase):
    """Test GET /drivers/ endpoint."""
    # Act
    response = test_app.get("/api/drivers/")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "123e4567-e89b-12d3-a456-426614174000"
    assert data[0]["first_name"] == "John"
    assert data[0]["last_name"] == "Doe"
    assert data[0]["email"] == "john.doe@example.com"


def test_get_driver_by_id(test_app, mock_supabase):
    """Test GET /drivers/{driver_id} endpoint."""
    # Arrange
    driver_id = "123e4567-e89b-12d3-a456-426614174000"
    
    # Act
    response = test_app.get(f"/api/drivers/{driver_id}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == driver_id
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john.doe@example.com"


def test_get_driver_by_id_not_found(test_app, mock_supabase):
    """Test GET /drivers/{driver_id} with non-existent ID."""
    # Arrange
    driver_id = "non-existent-id"
    
    # Act
    response = test_app.get(f"/api/drivers/{driver_id}")
    
    # Assert
    assert response.status_code == 404
    assert "detail" in response.json()


def test_create_driver(test_app, mock_supabase):
    """Test POST /drivers/ endpoint."""
    # Arrange
    driver_data = {
        "fleet_id": "123e4567-e89b-12d3-a456-426614174002",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone": "555-987-6543",
        "license_number": "DL98765432",
        "license_expiry": (datetime.now() + timedelta(days=365)).isoformat(),
        "date_of_birth": "1990-10-20",
        "date_hired": "2022-05-15",
        "status": "active",
        "address": "456 Park Ave, Anytown, USA",
        "emergency_contact_name": "John Smith",
        "emergency_contact_phone": "555-123-4567",
        "next_review_date": (datetime.now() + timedelta(days=90)).isoformat(),
        "notes": "New driver with excellent credentials"
    }
    
    # Act
    response = test_app.post("/api/drivers/", json=driver_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Smith"
    assert data["email"] == "jane.smith@example.com"


def test_update_driver(test_app, mock_supabase):
    """Test PUT /drivers/{driver_id} endpoint."""
    # Arrange
    driver_id = "123e4567-e89b-12d3-a456-426614174000"
    update_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.updated@example.com",
        "phone": "555-111-2222",
        "status": "inactive",
        "notes": "Updated driver information"
    }
    
    # Act
    response = test_app.put(f"/api/drivers/{driver_id}", json=update_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == driver_id
    assert data["email"] == "john.updated@example.com"
    assert data["phone"] == "555-111-2222"
    assert data["status"] == "inactive"
    assert data["notes"] == "Updated driver information"


def test_update_driver_not_found(test_app, mock_supabase):
    """Test PUT /drivers/{driver_id} with non-existent ID."""
    # Arrange
    driver_id = "non-existent-id"
    update_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.updated@example.com"
    }
    
    # Act
    response = test_app.put(f"/api/drivers/{driver_id}", json=update_data)
    
    # Assert
    assert response.status_code == 404
    assert "detail" in response.json()


def test_delete_driver(test_app, mock_supabase):
    """Test DELETE /drivers/{driver_id} endpoint."""
    # Arrange
    driver_id = "123e4567-e89b-12d3-a456-426614174000"
    
    # Act
    response = test_app.delete(f"/api/drivers/{driver_id}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True


def test_delete_driver_not_found(test_app, mock_supabase):
    """Test DELETE /drivers/{driver_id} with non-existent ID."""
    # Arrange
    driver_id = "non-existent-id"
    
    # Act
    response = test_app.delete(f"/api/drivers/{driver_id}")
    
    # Assert
    assert response.status_code == 404
    assert "detail" in response.json()


def test_get_drivers_by_fleet(test_app, mock_supabase):
    """Test GET /drivers/fleet/{fleet_id} endpoint."""
    # Arrange
    fleet_id = "123e4567-e89b-12d3-a456-426614174002"
    
    # Act
    response = test_app.get(f"/api/drivers/fleet/{fleet_id}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "123e4567-e89b-12d3-a456-426614174000"
    assert data[0]["fleet_id"] == fleet_id


def test_get_driver_stats(test_app, mock_supabase):
    """Test GET /drivers/{driver_id}/stats endpoint."""
    # Arrange
    driver_id = "123e4567-e89b-12d3-a456-426614174000"
    
    # Act
    response = test_app.get(f"/api/drivers/{driver_id}/stats")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total_trips"] == 25
    assert data["total_distance"] == 1200
    assert data["active_days"] == 20
    assert data["violations"] == 0
    assert data["incidents"] == 0
    assert data["fuel_consumption"] == 120
    assert data["efficiency_score"] == 92.5 