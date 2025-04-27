"""
Tests for the models module.
"""

import pytest
from datetime import datetime, date
from pydantic import ValidationError

from backend.models.driver import Driver, DriverCreate, DriverUpdate
from backend.models.vehicle import Vehicle, VehicleCreate, VehicleUpdate
from backend.models.fleet import Fleet, FleetCreate, FleetUpdate
from backend.models.transaction import Transaction, TransactionCreate, TransactionUpdate
from backend.models.organization import Organization, OrganizationCreate, OrganizationUpdate


def test_driver_model():
    """Test the Driver model."""
    # Test valid driver creation
    driver_data = {
        "id": "123e4567-e89b-12d3-a456-426614174004",
        "fleet_id": "123e4567-e89b-12d3-a456-426614174002",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "555-5678",
        "license_number": "DL123456",
        "license_expiry_date": "2025-01-01",
        "status": "active",
        "address": "456 Driver Street",
        "created_at": "2023-07-01T12:00:00Z",
        "updated_at": "2023-07-01T12:00:00Z"
    }
    
    driver = Driver(**driver_data)
    assert driver.id == "123e4567-e89b-12d3-a456-426614174004"
    assert driver.first_name == "John"
    assert driver.last_name == "Doe"
    assert driver.email == "john.doe@example.com"
    assert driver.license_expiry_date == date(2025, 1, 1)
    assert driver.status == "active"
    
    # Test DriverCreate
    driver_create_data = {
        "fleet_id": "123e4567-e89b-12d3-a456-426614174002",
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone_number": "555-9012",
        "license_number": "DL654321",
        "license_expiry_date": "2024-06-30",
        "status": "active",
        "address": "789 Driver Avenue"
    }
    
    driver_create = DriverCreate(**driver_create_data)
    assert driver_create.fleet_id == "123e4567-e89b-12d3-a456-426614174002"
    assert driver_create.first_name == "Jane"
    
    # Test DriverUpdate
    driver_update_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "status": "inactive"
    }
    
    driver_update = DriverUpdate(**driver_update_data)
    assert driver_update.first_name == "Jane"
    assert driver_update.status == "inactive"
    assert driver_update.last_name == "Smith"


def test_vehicle_model():
    """Test the Vehicle model."""
    # Test valid vehicle creation
    vehicle_data = {
        "id": "123e4567-e89b-12d3-a456-426614174003",
        "fleet_id": "123e4567-e89b-12d3-a456-426614174002",
        "make": "Toyota",
        "model": "Camry",
        "year": 2020,
        "vin": "1HGCM82633A123456",
        "license_plate": "ABC-1234",
        "status": "available",
        "color": "Blue",
        "fuel_type": "Gasoline",
        "mileage": 10000.0,
        "last_service_date": "2023-06-01T12:00:00Z",
        "next_service_date": "2023-12-01T12:00:00Z",
        "created_at": "2023-07-01T12:00:00Z",
        "updated_at": "2023-07-01T12:00:00Z"
    }
    
    vehicle = Vehicle(**vehicle_data)
    assert vehicle.id == "123e4567-e89b-12d3-a456-426614174003"
    assert vehicle.make == "Toyota"
    assert vehicle.model == "Camry"
    assert vehicle.year == 2020
    assert vehicle.status == "available"
    
    # Test VehicleCreate
    vehicle_create_data = {
        "fleet_id": "123e4567-e89b-12d3-a456-426614174002",
        "make": "Honda",
        "model": "Accord",
        "year": 2021,
        "vin": "1HGCM82633A654321",
        "license_plate": "XYZ-5678",
        "status": "available",
        "color": "Red",
        "fuel_type": "Gasoline",
        "mileage": 5000.0
    }
    
    vehicle_create = VehicleCreate(**vehicle_create_data)
    assert vehicle_create.fleet_id == "123e4567-e89b-12d3-a456-426614174002"
    assert vehicle_create.make == "Honda"
    
    # Test VehicleUpdate
    vehicle_update_data = {
        "status": "maintenance",
        "mileage": 15000.0,
        "last_service_date": "2023-07-15T12:00:00Z"
    }
    
    vehicle_update = VehicleUpdate(**vehicle_update_data)
    assert vehicle_update.status == "maintenance"
    assert vehicle_update.mileage == 15000.0


def test_fleet_model():
    """Test the Fleet model."""
    # Test valid fleet creation
    fleet_data = {
        "id": "123e4567-e89b-12d3-a456-426614174002",
        "name": "Test Fleet",
        "organization_id": "123e4567-e89b-12d3-a456-426614174001",
        "description": "Test fleet description",
        "location": "Test Location",
        "status": "active",
        "created_at": "2023-07-01T12:00:00Z",
        "updated_at": "2023-07-01T12:00:00Z"
    }
    
    fleet = Fleet(**fleet_data)
    assert fleet.id == "123e4567-e89b-12d3-a456-426614174002"
    assert fleet.name == "Test Fleet"
    assert fleet.organization_id == "123e4567-e89b-12d3-a456-426614174001"
    assert fleet.status == "active"
    
    # Test FleetCreate
    fleet_create_data = {
        "name": "New Fleet",
        "organization_id": "123e4567-e89b-12d3-a456-426614174001",
        "description": "New fleet description",
        "location": "New Location",
        "status": "active"
    }
    
    fleet_create = FleetCreate(**fleet_create_data)
    assert fleet_create.name == "New Fleet"
    assert fleet_create.organization_id == "123e4567-e89b-12d3-a456-426614174001"
    
    # Test FleetUpdate
    fleet_update_data = {
        "name": "Updated Fleet",
        "description": "Updated description",
        "status": "inactive"
    }
    
    fleet_update = FleetUpdate(**fleet_update_data)
    assert fleet_update.name == "Updated Fleet"
    assert fleet_update.description == "Updated description"
    assert fleet_update.status == "inactive"


def test_transaction_model():
    """Test the Transaction model."""
    # Test valid transaction creation
    transaction_data = {
        "id": "123e4567-e89b-12d3-a456-426614174005",
        "vehicle_id": "123e4567-e89b-12d3-a456-426614174003",
        "driver_id": "123e4567-e89b-12d3-a456-426614174004",
        "transaction_date": "2023-07-01T12:00:00Z",
        "transaction_type": "FUEL",
        "amount": 50.0,
        "description": "Fuel refill",
        "location": "Test Gas Station",
        "fuel_amount": 20.0,
        "fuel_type": "Gasoline",
        "odometer_reading": 10050.0,
        "created_at": "2023-07-01T12:00:00Z",
        "updated_at": "2023-07-01T12:00:00Z"
    }
    
    transaction = Transaction(**transaction_data)
    assert transaction.id == "123e4567-e89b-12d3-a456-426614174005"
    assert transaction.vehicle_id == "123e4567-e89b-12d3-a456-426614174003"
    assert transaction.driver_id == "123e4567-e89b-12d3-a456-426614174004"
    assert transaction.transaction_type == "FUEL"
    assert transaction.amount == 50.0
    
    # Test TransactionCreate
    transaction_create_data = {
        "vehicle_id": "123e4567-e89b-12d3-a456-426614174003",
        "driver_id": "123e4567-e89b-12d3-a456-426614174004",
        "transaction_date": "2023-07-15T12:00:00Z",
        "transaction_type": "MAINTENANCE",
        "amount": 200.0,
        "description": "Oil change",
        "location": "Test Garage",
        "odometer_reading": 10500.0
    }
    
    transaction_create = TransactionCreate(**transaction_create_data)
    assert transaction_create.vehicle_id == "123e4567-e89b-12d3-a456-426614174003"
    assert transaction_create.transaction_type == "MAINTENANCE"
    assert transaction_create.amount == 200.0
    
    # Test TransactionUpdate
    transaction_update_data = {
        "amount": 55.0,
        "description": "Updated description"
    }
    
    transaction_update = TransactionUpdate(**transaction_update_data)
    assert transaction_update.amount == 55.0
    assert transaction_update.description == "Updated description"


def test_organization_model():
    """Test the Organization model."""
    # Test valid organization creation
    organization_data = {
        "id": "123e4567-e89b-12d3-a456-426614174001",
        "name": "Test Organization",
        "address": "123 Test Street",
        "contact_email": "contact@testorg.com",
        "phone_number": "555-1234",
        "created_at": "2023-07-01T12:00:00Z",
        "updated_at": "2023-07-01T12:00:00Z"
    }
    
    organization = Organization(**organization_data)
    assert organization.id == "123e4567-e89b-12d3-a456-426614174001"
    assert organization.name == "Test Organization"
    assert organization.contact_email == "contact@testorg.com"
    
    # Test OrganizationCreate
    organization_create_data = {
        "name": "New Organization",
        "address": "456 New Street",
        "contact_email": "contact@neworg.com",
        "phone_number": "555-5678"
    }
    
    organization_create = OrganizationCreate(**organization_create_data)
    assert organization_create.name == "New Organization"
    assert organization_create.contact_email == "contact@neworg.com"
    
    # Test OrganizationUpdate
    organization_update_data = {
        "name": "Updated Organization",
        "address": "789 Updated Street"
    }
    
    organization_update = OrganizationUpdate(**organization_update_data)
    assert organization_update.name == "Updated Organization"
    assert organization_update.address == "789 Updated Street"


def test_invalid_models():
    """Test validation for invalid model data."""
    # Test invalid email
    with pytest.raises(ValidationError):
        Driver(
            id="123e4567-e89b-12d3-a456-426614174004",
            fleet_id="123e4567-e89b-12d3-a456-426614174002",
            first_name="John",
            last_name="Doe",
            email="invalid-email",  # Invalid email
            phone_number="555-5678",
            license_number="DL123456",
            license_expiry_date="2025-01-01",
            status="active",
            address="456 Driver Street",
            created_at="2023-07-01T12:00:00Z",
            updated_at="2023-07-01T12:00:00Z"
        )
    
    # Test invalid status
    with pytest.raises(ValidationError):
        Vehicle(
            id="123e4567-e89b-12d3-a456-426614174003",
            fleet_id="123e4567-e89b-12d3-a456-426614174002",
            make="Toyota",
            model="Camry",
            year=2020,
            vin="1HGCM82633A123456",
            license_plate="ABC-1234",
            status="invalid_status",  # Invalid status
            color="Blue",
            fuel_type="Gasoline",
            mileage=10000.0,
            created_at="2023-07-01T12:00:00Z",
            updated_at="2023-07-01T12:00:00Z"
        )
    
    # Test invalid year
    with pytest.raises(ValidationError):
        Vehicle(
            id="123e4567-e89b-12d3-a456-426614174003",
            fleet_id="123e4567-e89b-12d3-a456-426614174002",
            make="Toyota",
            model="Camry",
            year=1899,  # Year too old
            vin="1HGCM82633A123456",
            license_plate="ABC-1234",
            status="available",
            color="Blue",
            fuel_type="Gasoline",
            mileage=10000.0,
            created_at="2023-07-01T12:00:00Z",
            updated_at="2023-07-01T12:00:00Z"
        )
    
    # Test invalid transaction type
    with pytest.raises(ValidationError):
        Transaction(
            id="123e4567-e89b-12d3-a456-426614174005",
            vehicle_id="123e4567-e89b-12d3-a456-426614174003",
            driver_id="123e4567-e89b-12d3-a456-426614174004",
            transaction_date="2023-07-01T12:00:00Z",
            transaction_type="INVALID_TYPE",  # Invalid transaction type
            amount=50.0,
            description="Fuel refill",
            location="Test Gas Station",
            created_at="2023-07-01T12:00:00Z",
            updated_at="2023-07-01T12:00:00Z"
        ) 