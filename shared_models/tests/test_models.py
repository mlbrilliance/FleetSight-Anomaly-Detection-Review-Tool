"""
Tests for Pydantic models to ensure alignment with OWL ontology.
"""
import pytest
from decimal import Decimal
from datetime import datetime
from pydantic import ValidationError

from shared_models.models import (
    FleetTransaction, 
    FuelTransaction,
    MaintenanceTransaction,
    Vehicle,
    Driver
)

def test_fleet_transaction_validation():
    """Test validation rules for FleetTransaction model."""
    # Valid transaction
    transaction = FleetTransaction(
        transaction_id="tx123456",
        timestamp=datetime.now(),
        amount=Decimal("45.67"),
        currency="USD",
        merchant_name="Gas Station ABC",
        merchant_category="Fuel"
    )
    
    assert transaction.transaction_id == "tx123456"
    assert transaction.amount == Decimal("45.67")
    assert transaction.currency == "USD"
    
    # Invalid currency (lowercase)
    with pytest.raises(ValidationError) as exc_info:
        FleetTransaction(
            transaction_id="tx123456",
            timestamp=datetime.now(),
            amount=Decimal("45.67"),
            currency="usd",  # lowercase, should be uppercase per ISO 4217
            merchant_name="Gas Station ABC",
            merchant_category="Fuel"
        )
    assert "Currency code must be 3 uppercase letters" in str(exc_info.value)
    
    # Invalid amount (negative)
    with pytest.raises(ValidationError) as exc_info:
        FleetTransaction(
            transaction_id="tx123456",
            timestamp=datetime.now(),
            amount=Decimal("-45.67"),  # Negative amount not allowed
            currency="USD",
            merchant_name="Gas Station ABC",
            merchant_category="Fuel"
        )
    assert "ensure this value is greater than 0" in str(exc_info.value)
    
    # Invalid coordinates (only one provided)
    with pytest.raises(ValidationError) as exc_info:
        FleetTransaction(
            transaction_id="tx123456",
            timestamp=datetime.now(),
            amount=Decimal("45.67"),
            currency="USD",
            merchant_name="Gas Station ABC",
            merchant_category="Fuel",
            latitude=37.7749  # Missing longitude
        )
    assert "Both latitude and longitude must be provided together" in str(exc_info.value)

def test_fuel_transaction_validation():
    """Test FuelTransaction inherits and extends FleetTransaction properly."""
    # Valid fuel transaction
    fuel_txn = FuelTransaction(
        transaction_id="fuel123",
        timestamp=datetime.now(),
        amount=Decimal("50.00"),
        currency="USD",
        merchant_name="Shell Gas",
        merchant_category="Fuel",
        fuel_type="Unleaded",
        fuel_volume=Decimal("15.5"),
        fuel_volume_unit="gallon"
    )
    
    assert fuel_txn.transaction_id == "fuel123"
    assert fuel_txn.fuel_type == "Unleaded"
    assert fuel_txn.fuel_volume == Decimal("15.5")
    
    # Invalid fuel volume (zero or negative)
    with pytest.raises(ValidationError) as exc_info:
        FuelTransaction(
            transaction_id="fuel123",
            timestamp=datetime.now(),
            amount=Decimal("50.00"),
            currency="USD",
            merchant_name="Shell Gas",
            merchant_category="Fuel",
            fuel_type="Unleaded",
            fuel_volume=Decimal("0"),  # Zero not allowed
            fuel_volume_unit="gallon"
        )
    assert "ensure this value is greater than 0" in str(exc_info.value)

def test_maintenance_transaction_validation():
    """Test MaintenanceTransaction inherits and extends FleetTransaction properly."""
    # Valid maintenance transaction
    maint_txn = MaintenanceTransaction(
        transaction_id="maint123",
        timestamp=datetime.now(),
        amount=Decimal("150.00"),
        currency="USD",
        merchant_name="Auto Shop",
        merchant_category="Maintenance",
        maintenance_type="Oil Change",
        odometer_reading=45000
    )
    
    assert maint_txn.transaction_id == "maint123"
    assert maint_txn.maintenance_type == "Oil Change"
    assert maint_txn.odometer_reading == 45000

def test_vehicle_validation():
    """Test validation rules for Vehicle model."""
    # Valid vehicle
    vehicle = Vehicle(
        vehicle_id="V12345",
        make="Toyota",
        model="Camry",
        year=2020,
        vehicle_type="Sedan",
        fuel_capacity=Decimal("14.5"),
        fuel_capacity_unit="gallon"
    )
    
    assert vehicle.vehicle_id == "V12345"
    assert vehicle.make == "Toyota"
    assert vehicle.year == 2020
    
    # Invalid year (out of range)
    with pytest.raises(ValidationError) as exc_info:
        Vehicle(
            vehicle_id="V12345",
            make="Toyota",
            model="Camry",
            year=2200,  # Outside valid range
            vehicle_type="Sedan",
            fuel_capacity=Decimal("14.5"),
            fuel_capacity_unit="gallon"
        )
    assert "ensure this value is less than or equal to 2100" in str(exc_info.value)

def test_driver_validation():
    """Test validation rules for Driver model."""
    # Valid driver with no license (license optional)
    driver = Driver(
        driver_id="D5678",
        name="John Doe"
    )
    
    assert driver.driver_id == "D5678"
    assert driver.name == "John Doe"
    assert driver.license_number is None
    
    # Valid driver with optional fields
    driver_with_license = Driver(
        driver_id="D5678",
        name="John Doe",
        license_number="DL123456",
        assigned_vehicle_ids=["V12345", "V67890"]
    )
    
    assert driver_with_license.license_number == "DL123456"
    assert "V12345" in driver_with_license.assigned_vehicle_ids

def test_owl_mapping_metadata():
    """Test that models contain proper OWL mapping metadata."""
    for model_class in [FleetTransaction, FuelTransaction, MaintenanceTransaction, Vehicle, Driver]:
        schema = model_class.schema()
        assert "json_schema_extra" in schema
        assert "owl_mapping" in schema["json_schema_extra"]
        assert "source" in schema["json_schema_extra"]["owl_mapping"]
        assert "class" in schema["json_schema_extra"]["owl_mapping"]
        assert schema["json_schema_extra"]["owl_mapping"]["source"].startswith("owl/")
        
        # Verify class name matches OWL class
        class_name = model_class.__name__
        assert schema["json_schema_extra"]["owl_mapping"]["class"] == class_name 