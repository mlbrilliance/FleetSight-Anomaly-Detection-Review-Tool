"""
Tests for the transactions API endpoints.
"""

import json
import uuid
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from backend.api.v1.endpoints.transactions import get_db
from backend.db.interface import DatabaseInterface
from backend.main import app
from shared_models.models import FleetTransaction


class MockDB(DatabaseInterface):
    """Mock database for testing."""
    
    async def get_by_id(self, model_class, id):
        if id == "test-id":
            return FleetTransaction(
                id="test-id",
                driver_id="driver-1",
                vehicle_id="vehicle-1",
                amount=50.0,
                transaction_type="FUEL",
                timestamp="2023-01-01T12:00:00Z",
                location="Test Location",
                odometer_reading=12000,
                notes="Test transaction",
            )
        return None
    
    async def get_all(self, model_class):
        return [
            FleetTransaction(
                id="test-id-1",
                driver_id="driver-1",
                vehicle_id="vehicle-1",
                amount=50.0,
                transaction_type="FUEL",
                timestamp="2023-01-01T12:00:00Z",
                location="Test Location 1",
                odometer_reading=12000,
                notes="Test transaction 1",
            ),
            FleetTransaction(
                id="test-id-2",
                driver_id="driver-2",
                vehicle_id="vehicle-2",
                amount=75.0,
                transaction_type="MAINTENANCE",
                timestamp="2023-01-02T14:00:00Z",
                location="Test Location 2",
                odometer_reading=15000,
                notes="Test transaction 2",
            ),
        ]
    
    async def create(self, entity):
        return True, entity
    
    async def update(self, entity):
        return True, entity
    
    async def delete(self, model_class, id):
        return True
    
    async def search(self, model_class, criteria):
        return []
    
    async def batch_create(self, entities):
        return True, entities


# Override the get_db dependency for testing
app.dependency_overrides[get_db] = lambda: MockDB()

# Create test client
client = TestClient(app)


def test_create_transactions():
    """Test creating transactions."""
    # Test valid transactions
    test_transactions = [
        {
            "id": str(uuid.uuid4()),
            "driver_id": "driver-1",
            "vehicle_id": "vehicle-1",
            "amount": 50.0,
            "transaction_type": "FUEL",
            "timestamp": "2023-01-01T12:00:00Z",
            "location": "Test Location",
            "odometer_reading": 12000,
            "notes": "Test transaction",
        }
    ]
    
    response = client.post(
        "/api/v1/transactions/",
        json=test_transactions,
    )
    
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    assert response.json()["created"] == 1
    
    # Test empty transactions list
    response = client.post(
        "/api/v1/transactions/",
        json=[],
    )
    
    assert response.status_code == 400
    assert "No transactions provided" in response.json()["detail"]
    
    # Test invalid transaction (missing required field)
    invalid_transactions = [
        {
            "id": str(uuid.uuid4()),
            # Missing driver_id
            "vehicle_id": "vehicle-1",
            "amount": 50.0,
            "transaction_type": "FUEL",
            "timestamp": "2023-01-01T12:00:00Z",
        }
    ]
    
    response = client.post(
        "/api/v1/transactions/",
        json=invalid_transactions,
    )
    
    assert response.status_code == 422  # Validation error
    assert "field required" in json.dumps(response.json())


def test_get_transaction():
    """Test getting a transaction by ID."""
    # Test existing transaction
    response = client.get("/api/v1/transactions/test-id")
    
    assert response.status_code == 200
    assert response.json()["id"] == "test-id"
    assert response.json()["driver_id"] == "driver-1"
    
    # Test non-existent transaction
    response = client.get("/api/v1/transactions/non-existent-id")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_all_transactions():
    """Test getting all transactions."""
    response = client.get("/api/v1/transactions/")
    
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["id"] == "test-id-1"
    assert response.json()[1]["id"] == "test-id-2" 