"""
Transaction Data Cleaner and Preprocessor
[OWL: fleetsight-core-entities.ttl, fleetsight-ml.ttl, fleetsight-data-lineage.ttl]

This module implements preprocessing and cleaning functionality for transaction data.
It defines the ProcessedTransaction model and preprocess_data function which transform
raw transaction data into a format suitable for anomaly detection models.

All implementations align with the ontology definitions in the owl/ directory.
"""

import re
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Union, Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, root_validator, validator

from shared_models.models import FleetTransaction, FuelTransaction, MaintenanceTransaction


class ProcessedTransaction(BaseModel):
    """
    [OWL: fleetsight-ml.ttl#ProcessedData, fleetsight-data-lineage.ttl#PreprocessedDataset]
    
    Represents a transaction after preprocessing and cleaning, ready for anomaly detection.
    Contains only the fields relevant for anomaly detection with normalized values and 
    additional derived features.
    """
    # Core metadata preserved from original transaction
    transaction_id: str = Field(..., description="[OWL: core:transactionID] Original transaction ID")
    original_uuid: Optional[UUID] = Field(None, description="[OWL: core:entityUUID] Reference to original transaction UUID")
    
    # Timestamps and normalization
    timestamp: datetime = Field(..., description="[OWL: core:timestamp] When the transaction occurred")
    hour_of_day: int = Field(..., ge=0, lt=24, description="Hour component of timestamp, for time pattern analysis")
    day_of_week: int = Field(..., ge=0, lt=7, description="Day of week (0=Monday), for weekly pattern analysis")
    is_weekend: bool = Field(..., description="Whether transaction occurred on weekend")
    is_business_hours: bool = Field(..., description="Whether transaction occurred during business hours (8am-6pm)")
    
    # Transaction attributes with normalization
    amount: Decimal = Field(..., description="[OWL: core:amount] Monetary value in base currency")
    transaction_type: str = Field(..., description="[OWL: core:transactionType] Type of transaction")
    
    # Vehicle information
    vehicle_id: Optional[str] = Field(None, description="[OWL: core:transactionInvolvesVehicle] Related vehicle ID")
    
    # Driver information 
    driver_id: Optional[str] = Field(None, description="[OWL: core:transactionPerformedBy] Related driver ID")
    
    # Location-related features
    has_location: bool = Field(..., description="Whether transaction has valid location data")
    latitude: Optional[float] = Field(None, description="[OWL: core:latitude] Geographic latitude")
    longitude: Optional[float] = Field(None, description="[OWL: core:longitude] Geographic longitude")
    location_type: Optional[str] = Field(None, description="Derived location type (urban, rural, etc.)")
    
    # Fuel-specific normalized features 
    fuel_type: Optional[str] = Field(None, description="[OWL: core:fuelType] Type of fuel purchased")
    fuel_volume: Optional[Decimal] = Field(None, description="[OWL: core:fuelVolume] Volume in standard units")
    price_per_unit: Optional[Decimal] = Field(None, description="Calculated price per volume unit")
    
    # Maintenance-specific normalized features
    maintenance_type: Optional[str] = Field(None, description="[OWL: core:maintenanceType] Type of maintenance")
    
    # Derived features for anomaly detection
    days_since_last_transaction: Optional[int] = Field(None, description="Days elapsed since last transaction for this vehicle")
    distance_since_last_transaction: Optional[int] = Field(None, description="Estimated distance since last transaction")
    avg_consumption_rate: Optional[Decimal] = Field(None, description="For fuel: calculated consumption rate")

    class Config:
        json_schema_extra = {
            "owl_mapping": {
                "source": ["owl/fleetsight-ml.ttl", "owl/fleetsight-data-lineage.ttl"],
                "class": ["ProcessedData", "PreprocessedDataset"]
            }
        }


def _extract_time_features(timestamp: datetime) -> Dict[str, Any]:
    """
    Extract time-related features from a timestamp.
    
    Args:
        timestamp: The transaction timestamp
        
    Returns:
        Dictionary with time features
    """
    hour = timestamp.hour
    # Convert to 0-indexed day of week with Monday=0
    day_of_week = timestamp.weekday()  # Monday is 0
    is_weekend = day_of_week >= 5  # 5=Saturday, 6=Sunday
    is_business_hours = 8 <= hour < 18  # 8am-6pm
    
    return {
        "hour_of_day": hour,
        "day_of_week": day_of_week,
        "is_weekend": is_weekend,
        "is_business_hours": is_business_hours,
    }


def _extract_location_features(transaction: FleetTransaction) -> Dict[str, Any]:
    """
    Extract and normalize location features.
    
    Args:
        transaction: Original transaction
        
    Returns:
        Dictionary with location features
    """
    has_location = transaction.latitude is not None and transaction.longitude is not None
    location_type = None
    
    # Example of how we might derive location type (simplified)
    # This would be more sophisticated in a real implementation
    if has_location:
        # Simplified: Just an example placeholder derivation
        # In a real system, this would use more sophisticated geospatial analysis
        if abs(transaction.latitude) > 60:
            location_type = "remote"
        else:
            location_type = "standard"
    
    return {
        "has_location": has_location,
        "latitude": transaction.latitude,
        "longitude": transaction.longitude,
        "location_type": location_type,
    }


def _extract_fuel_features(transaction: FleetTransaction) -> Dict[str, Any]:
    """
    Extract fuel-specific features if applicable.
    
    Args:
        transaction: Original transaction
        
    Returns:
        Dictionary with fuel-specific features
    """
    result = {
        "fuel_type": None,
        "fuel_volume": None,
        "price_per_unit": None,
    }
    
    # Only extract fuel features for FuelTransaction objects
    if isinstance(transaction, FuelTransaction) and transaction.fuel_volume:
        result["fuel_type"] = transaction.fuel_type
        result["fuel_volume"] = transaction.fuel_volume
        
        # Calculate price per unit if we have volume and amount
        if transaction.amount and transaction.fuel_volume:
            try:
                result["price_per_unit"] = transaction.amount / transaction.fuel_volume
            except (ZeroDivisionError, TypeError):
                result["price_per_unit"] = None
    
    return result


def _extract_maintenance_features(transaction: FleetTransaction) -> Dict[str, Any]:
    """
    Extract maintenance-specific features if applicable.
    
    Args:
        transaction: Original transaction
        
    Returns:
        Dictionary with maintenance-specific features
    """
    result = {
        "maintenance_type": None,
    }
    
    if isinstance(transaction, MaintenanceTransaction):
        result["maintenance_type"] = transaction.maintenance_type
    
    return result


def _clean_text_fields(transaction: FleetTransaction) -> Dict[str, Any]:
    """
    Clean and normalize text fields.
    
    Args:
        transaction: Original transaction
        
    Returns:
        Dictionary with cleaned text fields
    """
    result = {}
    
    # Simple example of text cleaning - add more sophisticated cleaning as needed
    for field_name in ["merchant_name", "merchant_category", "notes"]:
        if hasattr(transaction, field_name) and getattr(transaction, field_name):
            value = getattr(transaction, field_name)
            if isinstance(value, str):
                # Convert to lowercase, trim whitespace, normalize spaces
                cleaned = re.sub(r'\s+', ' ', value.lower().strip())
                result[field_name] = cleaned
            else:
                result[field_name] = value
    
    return result


def preprocess_data(
    transaction: FleetTransaction,
    transaction_history: Optional[List[FleetTransaction]] = None
) -> ProcessedTransaction:
    """
    [OWL: fleetsight-ml.ttl#FeatureEngineeringStep, fleetsight-data-lineage.ttl#DataCleaningStep]
    
    Preprocess transaction data for anomaly detection.
    
    This function transforms raw transaction data into a clean, normalized format
    with derived features suitable for anomaly detection models. It handles different
    transaction types and calculates additional features based on history when available.
    
    Args:
        transaction: The transaction to preprocess
        transaction_history: Optional list of previous transactions for the same vehicle,
                             used to calculate relative features
    
    Returns:
        Processed transaction with normalized values and derived features
    """
    # Create a base dict with required fields
    base_data = {
        "transaction_id": transaction.transaction_id,
        "original_uuid": transaction.uuid if hasattr(transaction, "uuid") else None,
        "timestamp": transaction.timestamp,
        "amount": transaction.amount,
        "transaction_type": transaction.transaction_type,
        "vehicle_id": transaction.vehicle_id,
        "driver_id": transaction.driver_id,
    }
    
    # Extract features
    time_features = _extract_time_features(transaction.timestamp)
    location_features = _extract_location_features(transaction)
    fuel_features = _extract_fuel_features(transaction)
    maintenance_features = _extract_maintenance_features(transaction)
    
    # Combine all features
    processed_data = {
        **base_data,
        **time_features,
        **location_features,
        **fuel_features,
        **maintenance_features,
    }
    
    # Add derived features based on history if available
    if transaction_history and transaction.vehicle_id:
        # Filter history to just this vehicle and sort by timestamp
        vehicle_history = [
            t for t in transaction_history
            if t.vehicle_id == transaction.vehicle_id
            and t.timestamp < transaction.timestamp
        ]
        vehicle_history.sort(key=lambda t: t.timestamp, reverse=True)
        
        if vehicle_history:
            last_transaction = vehicle_history[0]
            days_diff = (transaction.timestamp - last_transaction.timestamp).days
            processed_data["days_since_last_transaction"] = days_diff
            
            # If both transactions have odometer readings, calculate distance
            if (hasattr(transaction, "odometer_reading") and hasattr(last_transaction, "odometer_reading") and
                    transaction.odometer_reading is not None and last_transaction.odometer_reading is not None):
                distance = transaction.odometer_reading - last_transaction.odometer_reading
                processed_data["distance_since_last_transaction"] = max(0, distance)
                
                # For fuel transactions, calculate consumption rate if possible
                if (isinstance(transaction, FuelTransaction) and transaction.fuel_volume and distance > 0):
                    processed_data["avg_consumption_rate"] = transaction.fuel_volume / (distance / 100)  # per 100 units
    
    # Create the processed transaction
    return ProcessedTransaction(**processed_data) 