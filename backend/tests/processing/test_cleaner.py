"""
Tests for cleaner.py
[OWL: fleetsight-core-entities.ttl, fleetsight-ml.ttl, fleetsight-data-lineage.ttl]

This module contains pytest-based tests for the transaction data preprocessing module.
These tests validate the preprocessing and feature extraction functionality.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from uuid import uuid4

from backend.processing.cleaner import (
    _extract_time_features,
    _extract_location_features,
    _extract_fuel_features,
    _extract_maintenance_features,
    _clean_text_fields,
    preprocess_data,
    ProcessedTransaction
)
from shared_models.models import FleetTransaction, FuelTransaction, MaintenanceTransaction


class MockFleetTransaction:
    """Mock base transaction class for testing."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockFuelTransaction(MockFleetTransaction):
    """Mock fuel transaction for testing."""
    pass


class MockMaintenanceTransaction(MockFleetTransaction):
    """Mock maintenance transaction for testing."""
    pass


@pytest.fixture
def sample_transaction():
    """Returns a basic transaction for testing."""
    return MockFleetTransaction(
        uuid=uuid4(),
        transaction_id="TRX-123456",
        timestamp=datetime(2023, 5, 15, 14, 30, 0),  # Tuesday, 2:30 PM
        amount=Decimal("100.00"),
        transaction_type="STANDARD",
        vehicle_id="VEH-001",
        driver_id="DRV-001",
        latitude=40.7128,
        longitude=-74.0060,
        merchant_name="Test Merchant",
        merchant_category="FUEL",
        odometer_reading=50000,
        notes="Test transaction"
    )


@pytest.fixture
def sample_fuel_transaction():
    """Returns a fuel transaction for testing."""
    return MockFuelTransaction(
        uuid=uuid4(),
        transaction_id="FUEL-123456",
        timestamp=datetime(2023, 5, 15, 14, 30, 0),
        amount=Decimal("80.00"),
        transaction_type="FUEL",
        vehicle_id="VEH-001",
        driver_id="DRV-001",
        latitude=40.7128,
        longitude=-74.0060,
        merchant_name="Fuel Station",
        merchant_category="FUEL",
        fuel_type="DIESEL",
        fuel_volume=Decimal("40.00"),
        odometer_reading=50000,
        notes="Fuel transaction"
    )


@pytest.fixture
def sample_maintenance_transaction():
    """Returns a maintenance transaction for testing."""
    return MockMaintenanceTransaction(
        uuid=uuid4(),
        transaction_id="MAINT-123456",
        timestamp=datetime(2023, 5, 15, 14, 30, 0),
        amount=Decimal("150.00"),
        transaction_type="MAINTENANCE",
        vehicle_id="VEH-001",
        driver_id="DRV-001",
        latitude=40.7128,
        longitude=-74.0060,
        merchant_name="Service Center",
        merchant_category="MAINTENANCE",
        maintenance_type="OIL_CHANGE",
        odometer_reading=50000,
        notes="Maintenance transaction"
    )


@pytest.fixture
def transaction_history():
    """Returns a list of transaction history for testing."""
    return [
        # Older transaction, 10 days ago
        MockFleetTransaction(
            uuid=uuid4(),
            transaction_id="TRX-PREV1",
            timestamp=datetime(2023, 5, 5, 10, 0, 0),
            amount=Decimal("90.00"),
            transaction_type="FUEL",
            vehicle_id="VEH-001",
            driver_id="DRV-001",
            odometer_reading=49500
        ),
        # Even older transaction, 20 days ago
        MockFleetTransaction(
            uuid=uuid4(),
            transaction_id="TRX-PREV2",
            timestamp=datetime(2023, 4, 25, 9, 0, 0),
            amount=Decimal("95.00"),
            transaction_type="MAINTENANCE",
            vehicle_id="VEH-001",
            driver_id="DRV-001",
            odometer_reading=49000
        )
    ]


def test_extract_time_features():
    """Test extraction of time-related features."""
    # Test a weekday (Tuesday) during business hours
    tuesday = datetime(2023, 5, 2, 14, 0, 0)  # Tuesday at 2 PM
    time_features = _extract_time_features(tuesday)
    
    assert time_features["hour_of_day"] == 14
    assert time_features["day_of_week"] == 1, "Monday is 0, so Tuesday should be 1"
    assert time_features["is_weekend"] is False
    assert time_features["is_business_hours"] is True
    
    # Test a weekend (Saturday) during business hours
    saturday = datetime(2023, 5, 6, 10, 0, 0)  # Saturday at 10 AM
    weekend_features = _extract_time_features(saturday)
    
    assert weekend_features["day_of_week"] == 5, "Saturday should be 5"
    assert weekend_features["is_weekend"] is True
    assert weekend_features["is_business_hours"] is True
    
    # Test outside business hours
    evening = datetime(2023, 5, 2, 20, 0, 0)  # Tuesday at 8 PM
    evening_features = _extract_time_features(evening)
    
    assert evening_features["hour_of_day"] == 20
    assert evening_features["is_business_hours"] is False


def test_extract_location_features(sample_transaction):
    """Test extraction of location-related features."""
    # Test with valid location data
    location_features = _extract_location_features(sample_transaction)
    
    assert location_features["has_location"] is True
    assert location_features["latitude"] == 40.7128
    assert location_features["longitude"] == -74.0060
    assert location_features["location_type"] is not None
    
    # Test without location data
    sample_transaction.latitude = None
    sample_transaction.longitude = None
    no_location_features = _extract_location_features(sample_transaction)
    
    assert no_location_features["has_location"] is False
    assert no_location_features["latitude"] is None
    assert no_location_features["longitude"] is None
    assert no_location_features["location_type"] is None


def test_extract_fuel_features(sample_transaction, sample_fuel_transaction):
    """Test extraction of fuel-related features."""
    # Test with regular transaction (not fuel)
    regular_features = _extract_fuel_features(sample_transaction)
    
    assert regular_features["fuel_type"] is None
    assert regular_features["fuel_volume"] is None
    assert regular_features["price_per_unit"] is None
    
    # Test with fuel transaction
    fuel_features = _extract_fuel_features(sample_fuel_transaction)
    
    assert fuel_features["fuel_type"] == "DIESEL"
    assert fuel_features["fuel_volume"] == Decimal("40.00")
    assert fuel_features["price_per_unit"] == Decimal("2.00"), "Price per unit should be 80/40 = 2"
    
    # Test with zero fuel volume (division by zero protection)
    sample_fuel_transaction.fuel_volume = Decimal("0")
    zero_volume_features = _extract_fuel_features(sample_fuel_transaction)
    
    assert zero_volume_features["price_per_unit"] is None, "Division by zero should return None"


def test_extract_maintenance_features(sample_transaction, sample_maintenance_transaction):
    """Test extraction of maintenance-related features."""
    # Test with regular transaction (not maintenance)
    regular_features = _extract_maintenance_features(sample_transaction)
    
    assert regular_features["maintenance_type"] is None
    
    # Test with maintenance transaction
    maintenance_features = _extract_maintenance_features(sample_maintenance_transaction)
    
    assert maintenance_features["maintenance_type"] == "OIL_CHANGE"


def test_clean_text_fields(sample_transaction):
    """Test cleaning of text fields."""
    # Set up text fields with mixed casing and extra whitespace
    sample_transaction.merchant_name = "Test  Merchant "
    sample_transaction.merchant_category = " FUEL "
    sample_transaction.notes = " This is a\n TEST note "
    
    cleaned = _clean_text_fields(sample_transaction)
    
    assert cleaned["merchant_name"] == "test merchant"
    assert cleaned["merchant_category"] == "fuel"
    assert cleaned["notes"] == "this is a test note"
    
    # Test with non-string values
    sample_transaction.merchant_name = None
    sample_transaction.notes = 123
    
    cleaned_with_non_strings = _clean_text_fields(sample_transaction)
    
    assert cleaned_with_non_strings["merchant_name"] is None
    assert cleaned_with_non_strings["notes"] == 123


def test_preprocess_data_basic(sample_transaction):
    """Test basic preprocessing without history."""
    processed = preprocess_data(sample_transaction)
    
    # Check that required fields are present
    assert processed.transaction_id == "TRX-123456"
    assert processed.original_uuid == sample_transaction.uuid
    assert processed.timestamp == sample_transaction.timestamp
    assert processed.amount == sample_transaction.amount
    assert processed.transaction_type == sample_transaction.transaction_type
    assert processed.vehicle_id == sample_transaction.vehicle_id
    assert processed.driver_id == sample_transaction.driver_id
    
    # Check extracted time features
    assert processed.hour_of_day == 14
    assert processed.day_of_week == 1  # Tuesday
    assert processed.is_weekend is False
    assert processed.is_business_hours is True
    
    # Check location features
    assert processed.has_location is True
    assert processed.latitude == 40.7128
    assert processed.longitude == -74.0060
    assert processed.location_type is not None
    
    # Check empty derived history fields
    assert processed.days_since_last_transaction is None
    assert processed.distance_since_last_transaction is None
    assert processed.avg_consumption_rate is None


def test_preprocess_data_with_history(sample_transaction, transaction_history):
    """Test preprocessing with transaction history."""
    processed = preprocess_data(sample_transaction, transaction_history)
    
    # Check derived history fields
    assert processed.days_since_last_transaction == 10, "Should be 10 days difference"
    assert processed.distance_since_last_transaction == 500, "Should be 50000 - 49500 = 500"


def test_preprocess_fuel_transaction(sample_fuel_transaction, transaction_history):
    """Test preprocessing of a fuel transaction with history."""
    processed = preprocess_data(sample_fuel_transaction, transaction_history)
    
    # Check fuel-specific fields
    assert processed.fuel_type == "DIESEL"
    assert processed.fuel_volume == Decimal("40.00")
    assert processed.price_per_unit == Decimal("2.00")
    
    # Check consumption rate calculation
    # 40 fuel units / (500 distance units / 100) = 8.0 units per 100 distance
    assert processed.avg_consumption_rate == Decimal("8.0"), "Consumption rate should be calculated from volume and distance"


def test_preprocess_maintenance_transaction(sample_maintenance_transaction):
    """Test preprocessing of a maintenance transaction."""
    processed = preprocess_data(sample_maintenance_transaction)
    
    # Check maintenance-specific fields
    assert processed.maintenance_type == "OIL_CHANGE"


def test_processed_transaction_model():
    """Test the ProcessedTransaction model validation."""
    # Create with minimal required fields
    processed = ProcessedTransaction(
        transaction_id="TEST-123",
        timestamp=datetime.now(),
        hour_of_day=12,
        day_of_week=3,
        is_weekend=False,
        is_business_hours=True,
        amount=Decimal("75.00"),
        transaction_type="TEST",
        has_location=False
    )
    
    # Verify fields
    assert processed.transaction_id == "TEST-123"
    assert processed.hour_of_day == 12
    assert processed.day_of_week == 3
    assert processed.is_weekend is False
    assert processed.is_business_hours is True
    assert processed.amount == Decimal("75.00")
    assert processed.transaction_type == "TEST"
    assert processed.has_location is False
    
    # Check optional fields are None
    assert processed.original_uuid is None
    assert processed.vehicle_id is None
    assert processed.driver_id is None
    assert processed.latitude is None
    assert processed.longitude is None
    assert processed.location_type is None
    assert processed.fuel_type is None
    assert processed.fuel_volume is None
    assert processed.price_per_unit is None
    assert processed.maintenance_type is None
    assert processed.days_since_last_transaction is None
    assert processed.distance_since_last_transaction is None
    assert processed.avg_consumption_rate is None


def test_owl_mapping_in_processed_transaction():
    """Test that OWL mapping is properly defined in the ProcessedTransaction model."""
    # Check OWL mapping in Config
    assert "owl_mapping" in ProcessedTransaction.Config.json_schema_extra
    owl_mapping = ProcessedTransaction.Config.json_schema_extra["owl_mapping"]
    
    assert "source" in owl_mapping
    assert "class" in owl_mapping
    
    sources = owl_mapping["source"]
    assert isinstance(sources, list)
    assert any("fleetsight-ml.ttl" in source for source in sources)
    assert any("fleetsight-data-lineage.ttl" in source for source in sources)
    
    classes = owl_mapping["class"]
    assert isinstance(classes, list)
    assert "ProcessedData" in classes
    assert "PreprocessedDataset" in classes 