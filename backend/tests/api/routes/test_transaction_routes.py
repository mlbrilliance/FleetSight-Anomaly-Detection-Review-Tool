"""
Tests for transaction_routes.py
[OWL: fleetsight-core-entities.ttl, fleetsight-anomaly.ttl]

This module contains tests for the transaction API endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from decimal import Decimal
from fastapi import status
from fastapi.testclient import TestClient

from backend.api.routes.transaction_routes import router, transaction_repo
from backend.models.transaction import Transaction
from backend.processing.cleaner import ProcessedTransaction
from shared_models.models import FleetTransaction, FuelTransaction


@pytest.fixture
def mock_user():
    """Returns a mock user for authentication."""
    return {"id": UUID("00000000-0000-0000-0000-000000000001"), "email": "test@example.com"}


@pytest.fixture
def mock_get_current_user(mock_user):
    """Mocks the get_current_user dependency."""
    with patch("backend.api.routes.transaction_routes.get_current_user", return_value=mock_user):
        yield


@pytest.fixture
def mock_transaction_repo():
    """Mocks the transaction repository."""
    with patch("backend.api.routes.transaction_routes.transaction_repo") as mock_repo:
        # Setup common mock return values
        mock_repo.list = AsyncMock()
        mock_repo.get = AsyncMock()
        mock_repo.create = AsyncMock()
        mock_repo.update = AsyncMock()
        mock_repo.delete = AsyncMock()
        mock_repo.find_by_driver = AsyncMock()
        mock_repo.find_by_vehicle = AsyncMock()
        mock_repo.find_by_date_range = AsyncMock()
        yield mock_repo


@pytest.fixture
def sample_transaction():
    """Returns a sample transaction for testing."""
    return Transaction(
        id=uuid4(),
        transaction_type="FUEL",
        amount=50.0,
        date=datetime.now(),
        created_at=datetime.now(),
        vehicle_id=uuid4(),
        driver_id=uuid4()
    )


@pytest.fixture
def sample_transactions():
    """Returns a list of sample transactions for testing."""
    return [
        Transaction(
            id=uuid4(),
            transaction_type="FUEL",
            amount=50.0,
            date=datetime.now(),
            created_at=datetime.now(),
            vehicle_id=uuid4(),
            driver_id=uuid4()
        ),
        Transaction(
            id=uuid4(),
            transaction_type="MAINTENANCE",
            amount=100.0,
            date=datetime.now(),
            created_at=datetime.now(),
            vehicle_id=uuid4(),
            driver_id=uuid4()
        )
    ]


@pytest.fixture
def sample_processed_transaction():
    """Returns a sample processed transaction for testing."""
    return ProcessedTransaction(
        transaction_id="123",
        timestamp=datetime.now(),
        hour_of_day=14,
        day_of_week=2,
        is_weekend=False,
        is_business_hours=True,
        amount=Decimal("50.00"),
        transaction_type="FUEL",
        has_location=True,
        latitude=40.7128,
        longitude=-74.0060,
    )


@pytest.fixture
def client(mock_get_current_user):
    """Creates a test client for the routes with mocked authentication."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


@pytest.mark.asyncio
async def test_get_all_transactions(client, mock_transaction_repo, sample_transactions):
    """Test GET /transactions/ endpoint."""
    # Setup
    mock_transaction_repo.list.return_value = sample_transactions
    
    # Execute
    response = client.get("/transactions/")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(sample_transactions)
    mock_transaction_repo.list.assert_called_once_with(skip=0, limit=100)


@pytest.mark.asyncio
async def test_get_transaction(client, mock_transaction_repo, sample_transaction):
    """Test GET /transactions/{transaction_id} endpoint."""
    # Setup
    transaction_id = sample_transaction.id
    mock_transaction_repo.get.return_value = sample_transaction
    
    # Execute
    response = client.get(f"/transactions/{transaction_id}")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == str(transaction_id)
    mock_transaction_repo.get.assert_called_once_with(transaction_id)


@pytest.mark.asyncio
async def test_get_transaction_not_found(client, mock_transaction_repo):
    """Test GET /transactions/{transaction_id} with non-existent ID."""
    # Setup
    transaction_id = uuid4()
    mock_transaction_repo.get.return_value = None
    
    # Execute
    response = client.get(f"/transactions/{transaction_id}")
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]
    mock_transaction_repo.get.assert_called_once_with(transaction_id)


@pytest.mark.asyncio
async def test_create_transaction(client, mock_transaction_repo, sample_transaction):
    """Test POST /transactions/ endpoint."""
    # Setup
    mock_transaction_repo.create.return_value = sample_transaction
    
    with patch("backend.api.routes.transaction_routes.preprocess_data") as mock_preprocess:
        mock_preprocess.return_value = MagicMock()
        
        # Execute
        response = client.post(
            "/transactions/",
            json={
                "id": str(sample_transaction.id),
                "transaction_type": sample_transaction.transaction_type,
                "amount": sample_transaction.amount,
                "date": sample_transaction.date.isoformat(),
                "created_at": sample_transaction.created_at.isoformat(),
                "vehicle_id": str(sample_transaction.vehicle_id),
                "driver_id": str(sample_transaction.driver_id)
            }
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert "transaction" in response.json()
        assert "processed_data" in response.json()
        mock_transaction_repo.create.assert_called_once()
        mock_preprocess.assert_called_once()


@pytest.mark.asyncio
async def test_create_transaction_without_preprocessing(client, mock_transaction_repo, sample_transaction):
    """Test POST /transactions/ endpoint without preprocessing."""
    # Setup
    mock_transaction_repo.create.return_value = sample_transaction
    
    # Execute
    response = client.post(
        "/transactions/?process_for_anomalies=false",
        json={
            "id": str(sample_transaction.id),
            "transaction_type": sample_transaction.transaction_type,
            "amount": sample_transaction.amount,
            "date": sample_transaction.date.isoformat(),
            "created_at": sample_transaction.created_at.isoformat(),
            "vehicle_id": str(sample_transaction.vehicle_id),
            "driver_id": str(sample_transaction.driver_id)
        }
    )
    
    # Assert
    assert response.status_code == status.HTTP_201_CREATED
    assert "transaction" in response.json()
    assert "processed_data" not in response.json()
    mock_transaction_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_transactions_batch(client, mock_transaction_repo, sample_transactions):
    """Test POST /transactions/batch endpoint."""
    # Setup
    mock_transaction_repo.create.side_effect = sample_transactions
    
    with patch("backend.api.routes.transaction_routes.preprocess_data") as mock_preprocess:
        mock_preprocess.return_value = MagicMock()
        
        # Execute
        response = client.post(
            "/transactions/batch",
            json=[
                {
                    "id": str(t.id),
                    "transaction_type": t.transaction_type,
                    "amount": t.amount,
                    "date": t.date.isoformat(),
                    "created_at": t.created_at.isoformat(),
                    "vehicle_id": str(t.vehicle_id),
                    "driver_id": str(t.driver_id)
                }
                for t in sample_transactions
            ]
        )
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["created"] == len(sample_transactions)
        assert "transactions" in response.json()
        assert "processed_data" in response.json()
        assert mock_transaction_repo.create.call_count == len(sample_transactions)
        assert mock_preprocess.call_count == len(sample_transactions)


@pytest.mark.asyncio
async def test_update_transaction(client, mock_transaction_repo, sample_transaction):
    """Test PUT /transactions/{transaction_id} endpoint."""
    # Setup
    transaction_id = sample_transaction.id
    mock_transaction_repo.get.return_value = sample_transaction
    mock_transaction_repo.update.return_value = sample_transaction
    
    with patch("backend.api.routes.transaction_routes.preprocess_data") as mock_preprocess:
        mock_preprocess.return_value = MagicMock()
        
        # Execute
        response = client.put(
            f"/transactions/{transaction_id}",
            json={
                "id": str(sample_transaction.id),
                "transaction_type": sample_transaction.transaction_type,
                "amount": sample_transaction.amount,
                "date": sample_transaction.date.isoformat(),
                "created_at": sample_transaction.created_at.isoformat(),
                "vehicle_id": str(sample_transaction.vehicle_id),
                "driver_id": str(sample_transaction.driver_id)
            }
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert "transaction" in response.json()
        assert "processed_data" in response.json()
        mock_transaction_repo.get.assert_called_once_with(transaction_id)
        mock_transaction_repo.update.assert_called_once()
        mock_preprocess.assert_called_once()


@pytest.mark.asyncio
async def test_update_transaction_not_found(client, mock_transaction_repo, sample_transaction):
    """Test PUT /transactions/{transaction_id} with non-existent ID."""
    # Setup
    transaction_id = uuid4()
    mock_transaction_repo.get.return_value = None
    
    # Execute
    response = client.put(
        f"/transactions/{transaction_id}",
        json={
            "id": str(sample_transaction.id),
            "transaction_type": sample_transaction.transaction_type,
            "amount": sample_transaction.amount,
            "date": sample_transaction.date.isoformat(),
            "created_at": sample_transaction.created_at.isoformat(),
            "vehicle_id": str(sample_transaction.vehicle_id),
            "driver_id": str(sample_transaction.driver_id)
        }
    )
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]
    mock_transaction_repo.get.assert_called_once_with(transaction_id)
    mock_transaction_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_delete_transaction(client, mock_transaction_repo, sample_transaction):
    """Test DELETE /transactions/{transaction_id} endpoint."""
    # Setup
    transaction_id = sample_transaction.id
    mock_transaction_repo.get.return_value = sample_transaction
    mock_transaction_repo.delete.return_value = True
    
    # Execute
    response = client.delete(f"/transactions/{transaction_id}")
    
    # Assert
    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_transaction_repo.get.assert_called_once_with(transaction_id)
    mock_transaction_repo.delete.assert_called_once_with(transaction_id)


@pytest.mark.asyncio
async def test_delete_transaction_not_found(client, mock_transaction_repo):
    """Test DELETE /transactions/{transaction_id} with non-existent ID."""
    # Setup
    transaction_id = uuid4()
    mock_transaction_repo.get.return_value = None
    
    # Execute
    response = client.delete(f"/transactions/{transaction_id}")
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]
    mock_transaction_repo.get.assert_called_once_with(transaction_id)
    mock_transaction_repo.delete.assert_not_called()


@pytest.mark.asyncio
async def test_delete_transaction_fail(client, mock_transaction_repo, sample_transaction):
    """Test DELETE /transactions/{transaction_id} with repository failure."""
    # Setup
    transaction_id = sample_transaction.id
    mock_transaction_repo.get.return_value = sample_transaction
    mock_transaction_repo.delete.return_value = False
    
    # Execute
    response = client.delete(f"/transactions/{transaction_id}")
    
    # Assert
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "Failed to delete" in response.json()["detail"]
    mock_transaction_repo.get.assert_called_once_with(transaction_id)
    mock_transaction_repo.delete.assert_called_once_with(transaction_id)


@pytest.mark.asyncio
async def test_get_transactions_by_driver(client, mock_transaction_repo, sample_transactions):
    """Test GET /transactions/driver/{driver_id} endpoint."""
    # Setup
    driver_id = uuid4()
    mock_transaction_repo.find_by_driver.return_value = sample_transactions
    
    # Execute
    response = client.get(f"/transactions/driver/{driver_id}")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(sample_transactions)
    mock_transaction_repo.find_by_driver.assert_called_once_with(driver_id, skip=0, limit=100)


@pytest.mark.asyncio
async def test_get_transactions_by_vehicle(client, mock_transaction_repo, sample_transactions):
    """Test GET /transactions/vehicle/{vehicle_id} endpoint."""
    # Setup
    vehicle_id = uuid4()
    mock_transaction_repo.find_by_vehicle.return_value = sample_transactions
    
    # Execute
    response = client.get(f"/transactions/vehicle/{vehicle_id}")
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(sample_transactions)
    mock_transaction_repo.find_by_vehicle.assert_called_once_with(vehicle_id, skip=0, limit=100)


@pytest.mark.asyncio
async def test_get_transactions_by_date_range(client, mock_transaction_repo, sample_transactions):
    """Test GET /transactions/date-range/ endpoint."""
    # Setup
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now()
    mock_transaction_repo.find_by_date_range.return_value = sample_transactions
    
    # Execute
    response = client.get(
        f"/transactions/date-range/?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}"
    )
    
    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(sample_transactions)
    mock_transaction_repo.find_by_date_range.assert_called_once_with(
        start_date=start_date, 
        end_date=end_date,
        skip=0,
        limit=100
    )


@pytest.mark.asyncio
async def test_process_transaction(client, mock_transaction_repo, sample_transaction, sample_processed_transaction):
    """Test POST /transactions/process/{transaction_id} endpoint."""
    # Setup
    transaction_id = sample_transaction.id
    mock_transaction_repo.get.return_value = sample_transaction
    
    with patch("backend.api.routes.transaction_routes.preprocess_data") as mock_preprocess:
        mock_preprocess.return_value = sample_processed_transaction
        
        # Execute
        response = client.post(f"/transactions/process/{transaction_id}")
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["transaction_id"] == sample_processed_transaction.transaction_id
        mock_transaction_repo.get.assert_called_once_with(transaction_id)
        mock_preprocess.assert_called_once()


@pytest.mark.asyncio
async def test_process_transaction_not_found(client, mock_transaction_repo):
    """Test POST /transactions/process/{transaction_id} with non-existent ID."""
    # Setup
    transaction_id = uuid4()
    mock_transaction_repo.get.return_value = None
    
    # Execute
    response = client.post(f"/transactions/process/{transaction_id}")
    
    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"]
    mock_transaction_repo.get.assert_called_once_with(transaction_id) 