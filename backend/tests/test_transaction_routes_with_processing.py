"""
Integration tests for transaction routes with processing functionality.

Tests the integration between transaction endpoints and the preprocessing functionality.
"""

import uuid
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
from decimal import Decimal

from backend.main import app
from backend.models.transaction import Transaction
from backend.models.user import User
from backend.processing.cleaner import ProcessedTransaction


@pytest.fixture
def mock_transaction_repo():
    """Create a mock transaction repository for testing."""
    mock_repo = MagicMock()
    
    # Mock create method
    async def mock_create(transaction):
        transaction.id = uuid.uuid4()
        return transaction
    mock_repo.create = AsyncMock(side_effect=mock_create)
    
    # Mock get method
    async def mock_get(id):
        return Transaction(
            id=id,
            vehicle_id=uuid.uuid4(),
            driver_id=uuid.uuid4(),
            transaction_type="FUEL",
            amount=Decimal("75.00"),
            date=datetime.now(),
            location="Test Location",
            created_at=datetime.now(),
        )
    mock_repo.get = AsyncMock(side_effect=mock_get)
    
    # Mock find_by_vehicle method
    async def mock_find_by_vehicle(vehicle_id, skip=0, limit=100):
        return [
            Transaction(
                id=uuid.uuid4(),
                vehicle_id=vehicle_id,
                driver_id=uuid.uuid4(),
                transaction_type="FUEL",
                amount=Decimal("60.00"),
                date=datetime.now(),
                location="Previous Location",
                odometer_reading=50000,
                created_at=datetime.now(),
            )
        ]
    mock_repo.find_by_vehicle = AsyncMock(side_effect=mock_find_by_vehicle)
    
    # Mock list method
    async def mock_list(skip=0, limit=100):
        return [
            Transaction(
                id=uuid.uuid4(),
                vehicle_id=uuid.uuid4(),
                driver_id=uuid.uuid4(),
                transaction_type="FUEL",
                amount=Decimal("75.00"),
                date=datetime.now(),
                location="Test Location",
                created_at=datetime.now(),
            ),
            Transaction(
                id=uuid.uuid4(),
                vehicle_id=uuid.uuid4(),
                driver_id=uuid.uuid4(),
                transaction_type="MAINTENANCE",
                amount=Decimal("150.00"),
                date=datetime.now(),
                location="Service Center",
                created_at=datetime.now(),
            )
        ]
    mock_repo.list = AsyncMock(side_effect=mock_list)
    
    return mock_repo


@pytest.fixture
def mock_current_user():
    """Create a mock current user for testing."""
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User",
        role="admin",
        is_active=True,
        created_at=datetime.now().isoformat()
    )


@pytest.fixture
def test_client(mock_transaction_repo, mock_current_user):
    """Create a test client with mocked dependencies."""
    # Patch the transaction repository
    with patch("backend.api.routes.transaction_routes.transaction_repo", mock_transaction_repo):
        # Patch the current user dependency
        with patch("backend.api.routes.transaction_routes.get_current_user", return_value=mock_current_user):
            client = TestClient(app)
            yield client


def test_create_transaction_with_processing(test_client, mock_transaction_repo):
    """Test creating a transaction with processing enabled."""
    transaction_data = {
        "vehicle_id": str(uuid.uuid4()),
        "driver_id": str(uuid.uuid4()),
        "transaction_type": "FUEL",
        "amount": 75.0,
        "date": datetime.now().isoformat(),
        "location": "Test Gas Station",
        "odometer_reading": 55000,
        "reference_number": "REF-12345"
    }
    
    # Test with processing enabled (default)
    response = test_client.post("/api/transactions/", json=transaction_data)
    assert response.status_code == 201
    
    data = response.json()
    assert "transaction" in data
    assert "processed_data" in data
    
    # Verify processed data
    processed_data = data["processed_data"]
    assert processed_data["transaction_type"] == "FUEL"
    assert "hour_of_day" in processed_data
    assert "day_of_week" in processed_data
    assert "is_weekend" in processed_data
    assert "is_business_hours" in processed_data
    
    # Verify transaction_repo.create was called
    mock_transaction_repo.create.assert_called_once()
    
    # Verify the vehicle history was retrieved for preprocessing
    mock_transaction_repo.find_by_vehicle.assert_called_once()


def test_create_transaction_without_processing(test_client, mock_transaction_repo):
    """Test creating a transaction with processing disabled."""
    transaction_data = {
        "vehicle_id": str(uuid.uuid4()),
        "driver_id": str(uuid.uuid4()),
        "transaction_type": "MAINTENANCE",
        "amount": 150.0,
        "date": datetime.now().isoformat(),
        "location": "Service Center",
        "reference_number": "SERV-789"
    }
    
    # Test with processing disabled
    response = test_client.post("/api/transactions/?process_for_anomalies=false", json=transaction_data)
    assert response.status_code == 201
    
    data = response.json()
    assert "transaction" in data
    assert "processed_data" not in data
    
    # Verify transaction_repo.create was called
    mock_transaction_repo.create.assert_called_once()
    
    # Verify the vehicle history was NOT retrieved
    mock_transaction_repo.find_by_vehicle.assert_not_called()


def test_batch_transaction_creation(test_client, mock_transaction_repo):
    """Test batch creation of transactions with processing."""
    transactions_data = [
        {
            "vehicle_id": str(uuid.uuid4()),
            "driver_id": str(uuid.uuid4()),
            "transaction_type": "FUEL",
            "amount": 75.0,
            "date": datetime.now().isoformat(),
            "location": "Gas Station 1",
            "odometer_reading": 55000
        },
        {
            "vehicle_id": str(uuid.uuid4()),
            "driver_id": str(uuid.uuid4()),
            "transaction_type": "MAINTENANCE",
            "amount": 120.0,
            "date": datetime.now().isoformat(),
            "location": "Service Center 1"
        }
    ]
    
    # Test batch creation with processing
    response = test_client.post("/api/transactions/batch", json=transactions_data)
    assert response.status_code == 201
    
    data = response.json()
    assert "created" in data
    assert data["created"] == 2
    assert "transactions" in data
    assert "processed_data" in data
    assert len(data["processed_data"]) == 2
    
    # First transaction is fuel, second is maintenance
    assert data["processed_data"][0]["transaction_type"] == "FUEL"
    assert data["processed_data"][1]["transaction_type"] == "MAINTENANCE"
    
    # Verify transaction_repo.create was called twice
    assert mock_transaction_repo.create.call_count == 2


def test_update_transaction_with_processing(test_client, mock_transaction_repo):
    """Test updating a transaction with processing."""
    transaction_id = uuid.uuid4()
    update_data = {
        "vehicle_id": str(uuid.uuid4()),
        "driver_id": str(uuid.uuid4()),
        "transaction_type": "FUEL",
        "amount": 85.0,
        "date": datetime.now().isoformat(),
        "location": "Updated Gas Station",
        "odometer_reading": 56000
    }
    
    # Mock update method
    async def mock_update(id, transaction):
        transaction.id = id
        return transaction
    mock_transaction_repo.update = AsyncMock(side_effect=mock_update)
    
    # Test update with processing
    response = test_client.put(f"/api/transactions/{transaction_id}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "transaction" in data
    assert "processed_data" in data
    
    # Verify processed data
    processed_data = data["processed_data"]
    assert processed_data["transaction_type"] == "FUEL"
    
    # Verify get and update were called
    mock_transaction_repo.get.assert_called_once_with(transaction_id)
    mock_transaction_repo.update.assert_called_once()


def test_process_existing_transaction(test_client, mock_transaction_repo):
    """Test processing an existing transaction."""
    transaction_id = uuid.uuid4()
    
    # Test processing endpoint
    response = test_client.post(f"/api/transactions/process/{transaction_id}")
    assert response.status_code == 200
    
    # Verify result is a ProcessedTransaction
    processed_data = response.json()
    assert "transaction_id" in processed_data
    assert "hour_of_day" in processed_data
    assert "day_of_week" in processed_data
    assert "is_weekend" in processed_data
    assert "transaction_type" in processed_data
    
    # Verify get was called for the transaction and its vehicle history
    mock_transaction_repo.get.assert_called_once_with(transaction_id)
    mock_transaction_repo.find_by_vehicle.assert_called_once() 