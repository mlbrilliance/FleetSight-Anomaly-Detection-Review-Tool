"""
Simplified tests for the processing.cleaner module.

This module tests the data preprocessing and cleaning functionality
without depending on the entire application.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from decimal import Decimal
from typing import Dict, Any

# Mock classes to avoid dependencies
class BaseMockTransaction:
    """Mock base transaction class for testing."""
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockFleetTransaction(BaseMockTransaction):
    """Mock fleet transaction for testing."""
    pass


class MockFuelTransaction(MockFleetTransaction):
    """Mock fuel transaction for testing."""
    pass


class MockMaintenanceTransaction(MockFleetTransaction):
    """Mock maintenance transaction for testing."""
    pass


# Import the processing functions
from backend.processing.cleaner import (
    _extract_time_features,
    _extract_location_features,
    _extract_fuel_features,
    _extract_maintenance_features,
    ProcessedTransaction,
)


def test_extract_time_features():
    """Test time feature extraction."""
    # Test weekday (Tuesday)
    tuesday = datetime(2023, 5, 2, 14, 0, 0)  # Tuesday at 2 PM
    time_features = _extract_time_features(tuesday)
    
    assert time_features["hour_of_day"] == 14
    assert time_features["day_of_week"] == 1  # Monday is 0, so Tuesday is 1
    assert time_features["is_weekend"] is False
    assert time_features["is_business_hours"] is True
    
    # Test weekend (Saturday)
    saturday = datetime(2023, 5, 6, 10, 0, 0)  # Saturday at 10 AM
    weekend_features = _extract_time_features(saturday)
    
    assert weekend_features["day_of_week"] == 5  # Saturday is 5
    assert weekend_features["is_weekend"] is True
    
    # Test outside business hours
    evening = datetime(2023, 5, 2, 20, 0, 0)  # Tuesday at 8 PM
    evening_features = _extract_time_features(evening)
    
    assert evening_features["is_business_hours"] is False


def test_extract_location_features():
    """Test location feature extraction."""
    # Transaction with location
    transaction_with_location = MockFleetTransaction(
        latitude=40.7128,
        longitude=-74.0060,
    )
    
    location_features = _extract_location_features(transaction_with_location)
    assert location_features["has_location"] is True
    assert location_features["latitude"] == 40.7128
    assert location_features["longitude"] == -74.0060
    assert location_features["location_type"] is not None
    
    # Transaction without location
    transaction_without_location = MockFleetTransaction(
        latitude=None,
        longitude=None,
    )
    
    no_location_features = _extract_location_features(transaction_without_location)
    assert no_location_features["has_location"] is False
    assert no_location_features["latitude"] is None
    assert no_location_features["longitude"] is None


def test_extract_fuel_features():
    """Test fuel feature extraction."""
    # Regular transaction (not fuel)
    regular_transaction = MockFleetTransaction()
    regular_features = _extract_fuel_features(regular_transaction)
    
    assert regular_features["fuel_type"] is None
    assert regular_features["fuel_volume"] is None
    assert regular_features["price_per_unit"] is None
    
    # Fuel transaction
    fuel_transaction = MockFuelTransaction(
        fuel_type="DIESEL",
        fuel_volume=Decimal("40.00"),
        amount=Decimal("80.00"),
    )
    
    fuel_features = _extract_fuel_features(fuel_transaction)
    assert fuel_features["fuel_type"] == "DIESEL"
    assert fuel_features["fuel_volume"] == Decimal("40.00")
    assert fuel_features["price_per_unit"] == Decimal("2.00")  # 80 / 40 = 2


def test_extract_maintenance_features():
    """Test maintenance feature extraction."""
    # Regular transaction (not maintenance)
    regular_transaction = MockFleetTransaction()
    regular_features = _extract_maintenance_features(regular_transaction)
    
    assert regular_features["maintenance_type"] is None
    
    # Maintenance transaction
    maintenance_transaction = MockMaintenanceTransaction(
        maintenance_type="OIL_CHANGE",
    )
    
    maintenance_features = _extract_maintenance_features(maintenance_transaction)
    assert maintenance_features["maintenance_type"] == "OIL_CHANGE"


def test_processed_transaction_model():
    """Test ProcessedTransaction model."""
    # Create a ProcessedTransaction with required fields
    transaction_id = str(uuid4())
    processed = ProcessedTransaction(
        transaction_id=transaction_id,
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
    
    # Check required fields
    assert processed.transaction_id == transaction_id
    assert processed.hour_of_day == 14
    assert processed.day_of_week == 2
    assert processed.is_weekend is False
    assert processed.is_business_hours is True
    assert processed.amount == Decimal("50.00")
    assert processed.transaction_type == "FUEL"
    assert processed.has_location is True
    assert processed.latitude == 40.7128
    assert processed.longitude == -74.0060
    
    # Check OWL mapping in Config
    assert "owl_mapping" in ProcessedTransaction.Config.json_schema_extra
    assert "source" in ProcessedTransaction.Config.json_schema_extra["owl_mapping"]
    assert any("fleetsight-ml.ttl" in source for source in ProcessedTransaction.Config.json_schema_extra["owl_mapping"]["source"]) 