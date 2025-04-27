"""
Pydantic models for FleetSight core entities.
[OWL: fleetsight-core-entities.ttl]

This module defines data models that directly map to the OWL ontology.
Each model includes explicit references to the ontology terms.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, validator, confloat

class Entity(BaseModel):
    """
    [OWL: fleetsight-core-entities.ttl#Entity]
    Base class for all domain entities with common attributes.
    """
    uuid: Optional[UUID] = Field(
        None,
        description="UUID for internal entity tracking [OWL: core:entityUUID]"
    )

    class Config:
        json_schema_extra = {
            "owl_mapping": {
                "source": "owl/fleetsight-core-entities.ttl",
                "class": "Entity"
            }
        }

class FleetTransaction(Entity):
    """
    [OWL: fleetsight-core-entities.ttl#FleetTransaction]
    Represents any recorded financial or operational event related to a fleet vehicle or driver.
    """
    transaction_id: str = Field(
        ..., 
        description="Unique identifier for a transaction [OWL: core:transactionID]",
        max_length=36
    )
    timestamp: datetime = Field(
        ...,
        description="Date and time when the transaction occurred [OWL: core:timestamp]"
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        description="The monetary value of the transaction [OWL: core:amount]"
    )
    currency: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Currency code (e.g., USD, EUR) [OWL: core:currency]"
    )
    merchant_name: str = Field(
        ...,
        max_length=255,
        description="Name of the merchant where the transaction occurred [OWL: core:merchantName]"
    )
    merchant_category: str = Field(
        ...,
        description="Category of the merchant [OWL: core:merchantCategory]"
    )
    latitude: Optional[confloat(ge=-90, le=90)] = Field(  # type: ignore
        None,
        description="Geographic latitude of the transaction location [OWL: core:latitude]"
    )
    longitude: Optional[confloat(ge=-180, le=180)] = Field(  # type: ignore
        None,
        description="Geographic longitude of the transaction location [OWL: core:longitude]"
    )
    vehicle_id: Optional[str] = Field(
        None,
        description="Reference to the vehicle involved [OWL: core:transactionInvolvesVehicle]"
    )
    driver_id: Optional[str] = Field(
        None,
        description="Reference to the driver who performed the transaction [OWL: core:transactionPerformedBy]"
    )

    @validator('currency')
    def validate_currency(cls, v):
        """Validate currency codes according to ISO 4217 standard"""
        if not v.isalpha() or not v.isupper():
            raise ValueError('Currency code must be 3 uppercase letters (ISO 4217)')
        return v
    
    @validator('latitude', 'longitude')
    def coordinates_must_be_together(cls, v, values):
        """Ensure that if one coordinate is provided, the other is too"""
        if 'latitude' in values and 'longitude' in values:
            if (values['latitude'] is None) != (values['longitude'] is None):
                raise ValueError('Both latitude and longitude must be provided together')
        return v

    class Config:
        json_schema_extra = {
            "owl_mapping": {
                "source": "owl/fleetsight-core-entities.ttl",
                "class": "FleetTransaction"
            }
        }


class FuelTransaction(FleetTransaction):
    """
    [OWL: fleetsight-core-entities.ttl#FuelTransaction]
    A specific type of Fleet Transaction representing the purchase of fuel.
    """
    fuel_type: str = Field(
        ...,
        description="Type of fuel purchased [OWL: core:fuelType]"
    )
    fuel_volume: Decimal = Field(
        ...,
        gt=0,
        description="Volume of fuel purchased [OWL: core:fuelVolume]"
    )
    fuel_volume_unit: str = Field(
        ...,
        description="Unit for the fuel volume [OWL: core:fuelVolumeUnit]"
    )
    odometer_reading: Optional[int] = Field(
        None,
        gt=0,
        description="Vehicle odometer reading at time of transaction [OWL: core:odometerReading]"
    )

    class Config:
        json_schema_extra = {
            "owl_mapping": {
                "source": "owl/fleetsight-core-entities.ttl",
                "class": "FuelTransaction"
            }
        }


class MaintenanceTransaction(FleetTransaction):
    """
    [OWL: fleetsight-core-entities.ttl#MaintenanceTransaction]
    A specific type of Fleet Transaction representing vehicle maintenance or repair services.
    """
    maintenance_type: str = Field(
        ...,
        description="Description of maintenance performed [OWL: core:maintenanceType]"
    )
    odometer_reading: Optional[int] = Field(
        None,
        gt=0,
        description="Vehicle odometer reading at time of maintenance [OWL: core:odometerReading]"
    )

    class Config:
        json_schema_extra = {
            "owl_mapping": {
                "source": "owl/fleetsight-core-entities.ttl",
                "class": "MaintenanceTransaction"
            }
        }


class Vehicle(Entity):
    """
    [OWL: fleetsight-core-entities.ttl#Vehicle]
    Represents a vehicle within the managed fleet.
    """
    vehicle_id: str = Field(
        ..., 
        description="Unique identifier for the vehicle [OWL: core:vehicleID]"
    )
    make: str = Field(
        ..., 
        description="Manufacturer of the vehicle [OWL: core:vehicleMake]"
    )
    model: str = Field(
        ..., 
        description="Model name of the vehicle [OWL: core:vehicleModel]"
    )
    year: int = Field(
        ..., 
        ge=1900,
        le=2100,
        description="Model year of the vehicle [OWL: core:vehicleYear]"
    )
    vehicle_type: str = Field(
        ..., 
        description="General classification of the vehicle [OWL: core:vehicleType]"
    )
    fuel_capacity: Decimal = Field(
        ..., 
        gt=0,
        description="Vehicle's fuel tank capacity [OWL: core:fuelCapacity]"
    )
    fuel_capacity_unit: str = Field(
        ..., 
        description="Unit for fuel capacity [OWL: core:fuelCapacityUnit]"
    )

    class Config:
        json_schema_extra = {
            "owl_mapping": {
                "source": "owl/fleetsight-core-entities.ttl",
                "class": "Vehicle"
            }
        }


class Driver(Entity):
    """
    [OWL: fleetsight-core-entities.ttl#Driver]
    Represents a driver associated with the fleet.
    """
    driver_id: str = Field(
        ..., 
        description="Unique identifier for the driver [OWL: core:driverID]"
    )
    name: str = Field(
        ..., 
        description="Full name of the driver [OWL: core:driverName]"
    )
    license_number: Optional[str] = Field(
        None,
        description="Driver's license number (PII - Handle securely) [OWL: core:driverLicenseNumber]"
    )
    assigned_vehicle_ids: Optional[List[str]] = Field(
        None,
        description="IDs of vehicles assigned to this driver [OWL: core:assignedVehicle]"
    )

    class Config:
        json_schema_extra = {
            "owl_mapping": {
                "source": "owl/fleetsight-core-entities.ttl",
                "class": "Driver"
            }
        } 