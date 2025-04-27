"""
Tests for the Supabase client implementation.
"""

import uuid
from unittest import mock

import pytest
from pydantic import BaseModel

from backend.db.supabase_client import SupabaseClient
from shared_models.models import Driver, FleetTransaction, Vehicle


class MockResponse:
    """Mock Supabase response object for testing."""
    
    def __init__(self, data=None):
        self.data = data or []


class MockQuery:
    """Mock Supabase query builder for testing."""
    
    def __init__(self, return_data=None):
        self.return_data = return_data or []
        self.conditions = []
    
    def select(self, *args):
        return self
    
    def insert(self, data):
        return self
    
    def update(self, data):
        return self
    
    def delete(self):
        return self
    
    def eq(self, field, value):
        self.conditions.append((field, value))
        return self
    
    def execute(self):
        return MockResponse(self.return_data)


class MockSupabaseClient:
    """Mock Supabase client for testing."""
    
    def __init__(self, return_data=None):
        self.return_data = return_data or []
    
    def table(self, table_name):
        return MockQuery(self.return_data)


@pytest.fixture
def mock_settings():
    """Patch settings for testing."""
    with mock.patch("backend.db.supabase_client.settings") as mock_settings:
        mock_settings.SUPABASE_URL = "https://example.supabase.co"
        mock_settings.SUPABASE_KEY = "fake-api-key"
        yield mock_settings


@pytest.fixture
def mock_supabase_client(mock_settings):
    """Create a SupabaseClient with mocked Supabase SDK."""
    with mock.patch("backend.db.supabase_client.create_client") as mock_create_client:
        mock_create_client.return_value = MockSupabaseClient()
        yield SupabaseClient()


def test_init_missing_settings():
    """Test that client initialization fails with missing settings."""
    with mock.patch("backend.db.supabase_client.settings") as mock_settings:
        mock_settings.SUPABASE_URL = None
        mock_settings.SUPABASE_KEY = None
        
        with pytest.raises(ValueError):
            SupabaseClient()


def test_get_table_for_model(mock_supabase_client):
    """Test that the correct table name is returned for model classes."""
    assert mock_supabase_client._get_table_for_model(Vehicle) == "vehicles"
    assert mock_supabase_client._get_table_for_model(Driver) == "drivers"
    assert mock_supabase_client._get_table_for_model(FleetTransaction) == "transactions"
    
    # Test invalid model class
    with pytest.raises(ValueError):
        mock_supabase_client._get_table_for_model(BaseModel)


@pytest.mark.asyncio
async def test_get_by_id(mock_supabase_client):
    """Test retrieving an entity by ID."""
    # Setup mock data
    test_id = str(uuid.uuid4())
    test_data = {"id": test_id, "name": "Test Vehicle", "make": "Test", "model": "X1"}
    
    # Mock the Supabase response
    mock_supabase_client.client = MockSupabaseClient([test_data])
    
    # Test successful retrieval
    result = await mock_supabase_client.get_by_id(Vehicle, test_id)
    assert result is not None
    assert result.id == test_id
    assert result.name == "Test Vehicle"
    
    # Test retrieval of non-existent entity
    mock_supabase_client.client = MockSupabaseClient([])
    result = await mock_supabase_client.get_by_id(Vehicle, test_id)
    assert result is None
    
    # Test exception handling
    with mock.patch.object(mock_supabase_client.client, "table", side_effect=Exception("Test error")):
        result = await mock_supabase_client.get_by_id(Vehicle, test_id)
        assert result is None


@pytest.mark.asyncio
async def test_get_all(mock_supabase_client):
    """Test retrieving all entities of a type."""
    # Setup mock data
    test_data = [
        {"id": str(uuid.uuid4()), "name": "Vehicle 1", "make": "Make 1", "model": "Model 1"},
        {"id": str(uuid.uuid4()), "name": "Vehicle 2", "make": "Make 2", "model": "Model 2"},
    ]
    
    # Mock the Supabase response
    mock_supabase_client.client = MockSupabaseClient(test_data)
    
    # Test successful retrieval
    results = await mock_supabase_client.get_all(Vehicle)
    assert len(results) == 2
    assert results[0].name == "Vehicle 1"
    assert results[1].name == "Vehicle 2"
    
    # Test empty response
    mock_supabase_client.client = MockSupabaseClient([])
    results = await mock_supabase_client.get_all(Vehicle)
    assert len(results) == 0
    
    # Test exception handling
    with mock.patch.object(mock_supabase_client.client, "table", side_effect=Exception("Test error")):
        results = await mock_supabase_client.get_all(Vehicle)
        assert len(results) == 0


@pytest.mark.asyncio
async def test_create(mock_supabase_client):
    """Test creating a new entity."""
    # Setup test entity
    test_id = str(uuid.uuid4())
    test_vehicle = Vehicle(id=test_id, name="Test Vehicle", make="Test", model="X1")
    
    # Setup mock response
    test_response_data = [test_vehicle.dict()]
    mock_supabase_client.client = MockSupabaseClient(test_response_data)
    
    # Test successful creation
    success, created = await mock_supabase_client.create(test_vehicle)
    assert success is True
    assert created is not None
    assert created.id == test_id
    
    # Test creation failure (empty response)
    mock_supabase_client.client = MockSupabaseClient([])
    success, created = await mock_supabase_client.create(test_vehicle)
    assert success is False
    assert created is None
    
    # Test exception handling
    with mock.patch.object(mock_supabase_client.client, "table", side_effect=Exception("Test error")):
        success, created = await mock_supabase_client.create(test_vehicle)
        assert success is False
        assert created is None


@pytest.mark.asyncio
async def test_update(mock_supabase_client):
    """Test updating an existing entity."""
    # Setup test entity
    test_id = str(uuid.uuid4())
    test_vehicle = Vehicle(id=test_id, name="Updated Vehicle", make="Test", model="X1")
    
    # Setup mock response
    test_response_data = [test_vehicle.dict()]
    mock_supabase_client.client = MockSupabaseClient(test_response_data)
    
    # Test successful update
    success, updated = await mock_supabase_client.update(test_vehicle)
    assert success is True
    assert updated is not None
    assert updated.name == "Updated Vehicle"
    
    # Test update failure (no ID)
    test_vehicle = Vehicle(name="No ID Vehicle", make="Test", model="X1")
    success, updated = await mock_supabase_client.update(test_vehicle)
    assert success is False
    assert updated is None
    
    # Test update failure (empty response)
    test_vehicle = Vehicle(id=test_id, name="Updated Vehicle", make="Test", model="X1")
    mock_supabase_client.client = MockSupabaseClient([])
    success, updated = await mock_supabase_client.update(test_vehicle)
    assert success is False
    assert updated is None
    
    # Test exception handling
    with mock.patch.object(mock_supabase_client.client, "table", side_effect=Exception("Test error")):
        success, updated = await mock_supabase_client.update(test_vehicle)
        assert success is False
        assert updated is None


@pytest.mark.asyncio
async def test_delete(mock_supabase_client):
    """Test deleting an entity."""
    # Setup test ID
    test_id = str(uuid.uuid4())
    
    # Setup mock response (success)
    mock_supabase_client.client = MockSupabaseClient([{"success": True}])
    
    # Test successful deletion
    success = await mock_supabase_client.delete(Vehicle, test_id)
    assert success is True
    
    # Test deletion failure (empty response)
    mock_supabase_client.client = MockSupabaseClient([])
    success = await mock_supabase_client.delete(Vehicle, test_id)
    assert success is False
    
    # Test exception handling
    with mock.patch.object(mock_supabase_client.client, "table", side_effect=Exception("Test error")):
        success = await mock_supabase_client.delete(Vehicle, test_id)
        assert success is False


@pytest.mark.asyncio
async def test_search(mock_supabase_client):
    """Test searching entities based on criteria."""
    # Setup mock data
    test_data = [
        {"id": str(uuid.uuid4()), "name": "Vehicle 1", "make": "Make 1", "model": "Model 1"},
        {"id": str(uuid.uuid4()), "name": "Vehicle 2", "make": "Make 2", "model": "Model 2"},
    ]
    
    # Mock the Supabase response
    mock_supabase_client.client = MockSupabaseClient(test_data)
    
    # Test successful search
    results = await mock_supabase_client.search(Vehicle, {"make": "Make 1"})
    assert len(results) == 2  # In our mock, the criteria are ignored
    
    # Test empty response
    mock_supabase_client.client = MockSupabaseClient([])
    results = await mock_supabase_client.search(Vehicle, {"make": "Make 1"})
    assert len(results) == 0
    
    # Test exception handling
    with mock.patch.object(mock_supabase_client.client, "table", side_effect=Exception("Test error")):
        results = await mock_supabase_client.search(Vehicle, {"make": "Make 1"})
        assert len(results) == 0


@pytest.mark.asyncio
async def test_batch_create(mock_supabase_client):
    """Test batch creation of entities."""
    # Setup test entities
    test_vehicles = [
        Vehicle(id=str(uuid.uuid4()), name="Vehicle 1", make="Make 1", model="Model 1"),
        Vehicle(id=str(uuid.uuid4()), name="Vehicle 2", make="Make 2", model="Model 2"),
    ]
    
    # Setup mock response
    test_response_data = [v.dict() for v in test_vehicles]
    mock_supabase_client.client = MockSupabaseClient(test_response_data)
    
    # Test successful batch creation
    success, created = await mock_supabase_client.batch_create(test_vehicles)
    assert success is True
    assert len(created) == 2
    
    # Test empty batch
    success, created = await mock_supabase_client.batch_create([])
    assert success is True
    assert len(created) == 0
    
    # Test batch creation failure (empty response)
    mock_supabase_client.client = MockSupabaseClient([])
    success, created = await mock_supabase_client.batch_create(test_vehicles)
    assert success is False
    assert len(created) == 0
    
    # Test exception handling
    with mock.patch.object(mock_supabase_client.client, "table", side_effect=Exception("Test error")):
        success, created = await mock_supabase_client.batch_create(test_vehicles)
        assert success is False
        assert len(created) == 0 