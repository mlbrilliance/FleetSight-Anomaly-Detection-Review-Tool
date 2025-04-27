"""
Direct test script for processing module.

This script directly tests the processing functionality without using pytest,
avoiding dependency issues.
"""

import sys
import os
from datetime import datetime
from uuid import uuid4
from decimal import Decimal
from typing import Dict, Any, List

# Add the backend directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

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


def run_tests():
    """Run all tests and report results."""
    tests = [
        test_extract_time_features,
        test_extract_location_features,
        test_extract_fuel_features,
        test_extract_maintenance_features,
        test_processed_transaction_model,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        print(f"Running test: {test_func.__name__}")
        try:
            test_func()
            print(f"✅ PASSED: {test_func.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {test_func.__name__} - {str(e)}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {test_func.__name__} - {str(e)}")
            failed += 1
        print("-" * 40)
    
    print(f"\nTest Results: {passed} passed, {failed} failed")
    return passed, failed


def assert_equal(actual, expected, message=None):
    """Simple assertion helper."""
    if actual != expected:
        error_msg = f"Expected {expected}, got {actual}"
        if message:
            error_msg = f"{message}: {error_msg}"
        raise AssertionError(error_msg)


def test_extract_time_features():
    """Test time feature extraction."""
    # Test weekday (Tuesday)
    tuesday = datetime(2023, 5, 2, 14, 0, 0)  # Tuesday at 2 PM
    time_features = _extract_time_features(tuesday)
    
    assert_equal(time_features["hour_of_day"], 14)
    assert_equal(time_features["day_of_week"], 1, "Monday is 0, so Tuesday should be 1")
    assert_equal(time_features["is_weekend"], False)
    assert_equal(time_features["is_business_hours"], True)
    
    # Test weekend (Saturday)
    saturday = datetime(2023, 5, 6, 10, 0, 0)  # Saturday at 10 AM
    weekend_features = _extract_time_features(saturday)
    
    assert_equal(weekend_features["day_of_week"], 5, "Saturday should be 5")
    assert_equal(weekend_features["is_weekend"], True)
    
    # Test outside business hours
    evening = datetime(2023, 5, 2, 20, 0, 0)  # Tuesday at 8 PM
    evening_features = _extract_time_features(evening)
    
    assert_equal(evening_features["is_business_hours"], False)


def test_extract_location_features():
    """Test location feature extraction."""
    # Transaction with location
    transaction_with_location = MockFleetTransaction(
        latitude=40.7128,
        longitude=-74.0060,
    )
    
    location_features = _extract_location_features(transaction_with_location)
    assert_equal(location_features["has_location"], True)
    assert_equal(location_features["latitude"], 40.7128)
    assert_equal(location_features["longitude"], -74.0060)
    assert location_features["location_type"] is not None, "location_type should not be None"
    
    # Transaction without location
    transaction_without_location = MockFleetTransaction(
        latitude=None,
        longitude=None,
    )
    
    no_location_features = _extract_location_features(transaction_without_location)
    assert_equal(no_location_features["has_location"], False)
    assert_equal(no_location_features["latitude"], None)
    assert_equal(no_location_features["longitude"], None)


def test_extract_fuel_features():
    """Test fuel feature extraction."""
    # Regular transaction (not fuel)
    regular_transaction = MockFleetTransaction()
    regular_features = _extract_fuel_features(regular_transaction)
    
    assert_equal(regular_features["fuel_type"], None)
    assert_equal(regular_features["fuel_volume"], None)
    assert_equal(regular_features["price_per_unit"], None)
    
    # Fuel transaction
    fuel_transaction = MockFuelTransaction(
        fuel_type="DIESEL",
        fuel_volume=Decimal("40.00"),
        amount=Decimal("80.00"),
    )
    
    fuel_features = _extract_fuel_features(fuel_transaction)
    assert_equal(fuel_features["fuel_type"], "DIESEL")
    assert_equal(fuel_features["fuel_volume"], Decimal("40.00"))
    assert_equal(fuel_features["price_per_unit"], Decimal("2.00"), "Price per unit should be 80/40 = 2")


def test_extract_maintenance_features():
    """Test maintenance feature extraction."""
    # Regular transaction (not maintenance)
    regular_transaction = MockFleetTransaction()
    regular_features = _extract_maintenance_features(regular_transaction)
    
    assert_equal(regular_features["maintenance_type"], None)
    
    # Maintenance transaction
    maintenance_transaction = MockMaintenanceTransaction(
        maintenance_type="OIL_CHANGE",
    )
    
    maintenance_features = _extract_maintenance_features(maintenance_transaction)
    assert_equal(maintenance_features["maintenance_type"], "OIL_CHANGE")


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
    assert_equal(processed.transaction_id, transaction_id)
    assert_equal(processed.hour_of_day, 14)
    assert_equal(processed.day_of_week, 2)
    assert_equal(processed.is_weekend, False)
    assert_equal(processed.is_business_hours, True)
    assert_equal(processed.amount, Decimal("50.00"))
    assert_equal(processed.transaction_type, "FUEL")
    assert_equal(processed.has_location, True)
    assert_equal(processed.latitude, 40.7128)
    assert_equal(processed.longitude, -74.0060)
    
    # Check OWL mapping in Config
    assert "owl_mapping" in ProcessedTransaction.Config.json_schema_extra, "ProcessedTransaction should have owl_mapping in Config"
    assert "source" in ProcessedTransaction.Config.json_schema_extra["owl_mapping"], "owl_mapping should have source field"
    sources = ProcessedTransaction.Config.json_schema_extra["owl_mapping"]["source"]
    assert any("fleetsight-ml.ttl" in source for source in sources), "owl_mapping source should include fleetsight-ml.ttl"


if __name__ == "__main__":
    run_tests() 