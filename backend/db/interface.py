"""
Database interface specification for FleetSight.
[OWL: fleetsight-core-entities.ttl, fleetsight-system.ttl]

This module defines the abstract base classes for database operations,
ensuring strict compliance with the ontology definitions.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union, Type, TypeVar
from uuid import UUID

from shared_models.models import (
    FleetTransaction, FuelTransaction, MaintenanceTransaction,
    Vehicle, Driver
)

T = TypeVar('T', FleetTransaction, FuelTransaction, MaintenanceTransaction, Vehicle, Driver)

class DBInterface(ABC):
    """
    Abstract database interface for the FleetSight application.
    [OWL: fleetsight-system.ttl#DataStorage]
    """
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the database."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if database connection is healthy."""
        pass

    # Transaction management methods
    @abstractmethod
    async def begin_transaction(self) -> None:
        """Begin a database transaction for atomic operations."""
        pass
    
    @abstractmethod
    async def commit_transaction(self) -> None:
        """Commit the current transaction."""
        pass
    
    @abstractmethod
    async def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        pass
    
    # Generic CRUD operations
    @abstractmethod
    async def create_entity(self, model: T) -> T:
        """
        Create a new entity in the database.
        
        Args:
            model: Pydantic model instance validated against ontology
            
        Returns:
            Created entity with database-assigned IDs
        """
        pass
    
    @abstractmethod
    async def get_entity_by_id(self, entity_type: Type[T], id_value: Union[str, UUID]) -> Optional[T]:
        """
        Retrieve an entity by its ID.
        
        Args:
            entity_type: The Pydantic model class (must match an ontology class)
            id_value: Business identifier or database UUID
            
        Returns:
            Entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update_entity(self, model: T) -> T:
        """
        Update an existing entity.
        
        Args:
            model: Pydantic model with updated values
            
        Returns:
            Updated entity
        """
        pass
    
    @abstractmethod
    async def delete_entity(self, entity_type: Type[T], id_value: Union[str, UUID]) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            entity_type: The Pydantic model class
            id_value: Business identifier or database UUID
            
        Returns:
            True if deleted, False if not found
        """
        pass


class TransactionRepository(ABC):
    """
    Repository for transaction-specific operations.
    [OWL: fleetsight-core-entities.ttl#FleetTransaction]
    """
    
    @abstractmethod
    async def create_transaction(self, transaction: FleetTransaction) -> FleetTransaction:
        """
        Create a new transaction with appropriate subtype handling.
        
        Args:
            transaction: Transaction model (can be subclass like FuelTransaction)
            
        Returns:
            Created transaction with database IDs
        """
        pass
    
    @abstractmethod
    async def get_transaction_by_id(self, transaction_id: str) -> Optional[FleetTransaction]:
        """
        Retrieve a transaction by its business identifier.
        
        Args:
            transaction_id: Business identifier from fs:transactionID
            
        Returns:
            Transaction if found (with proper subclass), None otherwise
        """
        pass
    
    @abstractmethod
    async def get_transactions_by_filter(
        self, 
        filter_params: Dict[str, Any], 
        limit: int = 100, 
        offset: int = 0
    ) -> List[FleetTransaction]:
        """
        Query transactions with filtering.
        
        Args:
            filter_params: Dictionary of filter criteria
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of matching transactions
        """
        pass
    
    @abstractmethod
    async def get_transactions_by_vehicle(
        self, 
        vehicle_id: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[FleetTransaction]:
        """
        Get transactions for a specific vehicle.
        [OWL: fleetsight-core-entities.ttl#transactionInvolvesVehicle]
        
        Args:
            vehicle_id: Vehicle business identifier
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of transactions associated with the vehicle
        """
        pass
    
    @abstractmethod
    async def get_transactions_by_driver(
        self, 
        driver_id: str, 
        limit: int = 100, 
        offset: int = 0
    ) -> List[FleetTransaction]:
        """
        Get transactions for a specific driver.
        [OWL: fleetsight-core-entities.ttl#transactionPerformedBy]
        
        Args:
            driver_id: Driver business identifier
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of transactions performed by the driver
        """
        pass
    
    @abstractmethod
    async def get_fuel_transactions(
        self, 
        filter_params: Dict[str, Any], 
        limit: int = 100, 
        offset: int = 0
    ) -> List[FuelTransaction]:
        """
        Get fuel transactions with filtering.
        [OWL: fleetsight-core-entities.ttl#FuelTransaction]
        
        Args:
            filter_params: Dictionary of filter criteria
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of fuel transactions
        """
        pass
    
    @abstractmethod
    async def batch_create_transactions(
        self, 
        transactions: List[FleetTransaction]
    ) -> List[FleetTransaction]:
        """
        Create multiple transactions in a single operation.
        
        Args:
            transactions: List of transaction models
            
        Returns:
            Created transactions with database IDs
        """
        pass


class VehicleRepository(ABC):
    """
    Repository for vehicle-specific operations.
    [OWL: fleetsight-core-entities.ttl#Vehicle]
    """
    
    @abstractmethod
    async def create_vehicle(self, vehicle: Vehicle) -> Vehicle:
        """Create a new vehicle."""
        pass
    
    @abstractmethod
    async def get_vehicle_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        """Retrieve a vehicle by business identifier."""
        pass
    
    @abstractmethod
    async def get_all_vehicles(self, limit: int = 100, offset: int = 0) -> List[Vehicle]:
        """Get all vehicles with pagination."""
        pass
    
    @abstractmethod
    async def update_vehicle(self, vehicle: Vehicle) -> Vehicle:
        """Update an existing vehicle."""
        pass
    
    @abstractmethod
    async def delete_vehicle(self, vehicle_id: str) -> bool:
        """Delete a vehicle by ID."""
        pass


class DriverRepository(ABC):
    """
    Repository for driver-specific operations.
    [OWL: fleetsight-core-entities.ttl#Driver]
    """
    
    @abstractmethod
    async def create_driver(self, driver: Driver) -> Driver:
        """Create a new driver."""
        pass
    
    @abstractmethod
    async def get_driver_by_id(self, driver_id: str) -> Optional[Driver]:
        """Retrieve a driver by business identifier."""
        pass
    
    @abstractmethod
    async def get_all_drivers(self, limit: int = 100, offset: int = 0) -> List[Driver]:
        """Get all drivers with pagination."""
        pass
    
    @abstractmethod
    async def get_drivers_by_vehicle(self, vehicle_id: str) -> List[Driver]:
        """
        Get drivers associated with a vehicle.
        [OWL: fleetsight-core-entities.ttl#assignedVehicle]
        """
        pass
    
    @abstractmethod
    async def update_driver(self, driver: Driver) -> Driver:
        """Update an existing driver."""
        pass
    
    @abstractmethod
    async def delete_driver(self, driver_id: str) -> bool:
        """Delete a driver by ID."""
        pass 