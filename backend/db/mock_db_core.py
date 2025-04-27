"""
MockDB Core Implementation for the FleetSight Backend
[OWL: fleetsight-system.ttl#MockDatabase]

This module implements the core functionality of the mock database with in-memory storage.
It provides connection management, transaction handling, and generic entity operations.
"""
import asyncio
import copy
import uuid
from typing import Dict, List, Type, TypeVar, Optional, Any, Generic, cast

from shared_models.models import (
    FleetTransaction, FuelTransaction, MaintenanceTransaction,
    Vehicle, Driver, Entity
)
from backend.db.interface import (
    DBInterface, TransactionRepository, VehicleRepository, DriverRepository
)

T = TypeVar('T', bound=Entity)


class MockDBCore(DBInterface):
    """
    Mock database core implementation with in-memory storage.
    
    This class implements connection management, transaction handling,
    and generic entity operations.
    
    [OWL: fleetsight-system.ttl#MockDatabase]
    """
    
    def __init__(self):
        """
        Initialize the mock database with empty storage.
        Sets up in-memory dictionaries for entities and prepares transaction support.
        """
        # Main storage dictionaries
        self._vehicles: Dict[str, Vehicle] = {}
        self._drivers: Dict[str, Driver] = {}
        self._transactions: Dict[str, FleetTransaction] = {}
        
        # UUID lookup dictionaries for efficient retrieval
        self._vehicle_uuids: Dict[uuid.UUID, str] = {}
        self._driver_uuids: Dict[uuid.UUID, str] = {}
        self._transaction_uuids: Dict[uuid.UUID, str] = {}
        
        # Transaction support
        self._in_transaction = False
        self._transaction_backup = {
            'vehicles': {},
            'drivers': {},
            'transactions': {}
        }
        
        # Connected state
        self._connected = False
    
    async def connect(self) -> bool:
        """
        Connect to the mock database and initialize test data.
        
        Returns:
            bool: True if connection successful
        """
        self._connected = True
        await self._populate_test_data()
        return True
    
    async def disconnect(self) -> bool:
        """
        Disconnect from the mock database.
        
        Returns:
            bool: True if disconnection successful
        """
        self._connected = False
        return True
    
    async def health_check(self) -> bool:
        """
        Check if the database is healthy and available.
        
        Returns:
            bool: True if database is healthy
        """
        return self._connected
    
    async def begin_transaction(self) -> bool:
        """
        Start a transaction. Changes will be isolated until commit or rollback.
        
        Returns:
            bool: True if transaction started successfully
        
        Raises:
            RuntimeError: If a transaction is already in progress
        """
        if self._in_transaction:
            raise RuntimeError("Transaction already in progress")
        
        # Create deep copies of current data as backup
        self._transaction_backup = {
            'vehicles': copy.deepcopy(self._vehicles),
            'drivers': copy.deepcopy(self._drivers),
            'transactions': copy.deepcopy(self._transactions)
        }
        
        self._in_transaction = True
        return True
    
    async def commit_transaction(self) -> bool:
        """
        Commit the current transaction, making changes permanent.
        
        Returns:
            bool: True if transaction committed successfully
        
        Raises:
            RuntimeError: If no transaction is in progress
        """
        if not self._in_transaction:
            raise RuntimeError("No transaction in progress")
        
        # Clear the backup since we're committing changes
        self._transaction_backup = {
            'vehicles': {},
            'drivers': {},
            'transactions': {}
        }
        
        self._in_transaction = False
        return True
    
    async def rollback_transaction(self) -> bool:
        """
        Rollback the current transaction, discarding all changes.
        
        Returns:
            bool: True if transaction rolled back successfully
        
        Raises:
            RuntimeError: If no transaction is in progress
        """
        if not self._in_transaction:
            raise RuntimeError("No transaction in progress")
        
        # Restore data from backup
        self._vehicles = self._transaction_backup['vehicles']
        self._drivers = self._transaction_backup['drivers']
        self._transactions = self._transaction_backup['transactions']
        
        # Rebuild UUID lookup tables
        self._rebuild_uuid_lookups()
        
        self._in_transaction = False
        return True
    
    def _rebuild_uuid_lookups(self) -> None:
        """Rebuild UUID lookup dictionaries after a rollback."""
        # Clear existing lookups
        self._vehicle_uuids = {}
        self._driver_uuids = {}
        self._transaction_uuids = {}
        
        # Rebuild vehicle lookups
        for vehicle_id, vehicle in self._vehicles.items():
            if hasattr(vehicle, 'uuid') and vehicle.uuid:
                self._vehicle_uuids[vehicle.uuid] = vehicle_id
        
        # Rebuild driver lookups
        for driver_id, driver in self._drivers.items():
            if hasattr(driver, 'uuid') and driver.uuid:
                self._driver_uuids[driver.uuid] = driver_id
        
        # Rebuild transaction lookups
        for txn_id, txn in self._transactions.items():
            if hasattr(txn, 'uuid') and txn.uuid:
                self._transaction_uuids[txn.uuid] = txn_id
    
    # Generic entity operations
    
    async def create_entity(self, entity: T) -> T:
        """
        Generic method to create any entity in the database.
        
        Args:
            entity: The entity to create
            
        Returns:
            The created entity
            
        Raises:
            ValueError: If entity already exists or has invalid references
        """
        if isinstance(entity, Vehicle):
            return await self.create_vehicle(entity)
        elif isinstance(entity, Driver):
            return await self.create_driver(entity)
        elif isinstance(entity, FleetTransaction):
            return await self.create_transaction(entity)
        else:
            raise ValueError(f"Unsupported entity type: {type(entity)}")
    
    async def get_entity_by_id(self, entity_type: Type[T], entity_id: str) -> Optional[T]:
        """
        Generic method to retrieve any entity by its ID.
        
        Args:
            entity_type: The type of entity to retrieve
            entity_id: The ID of the entity
            
        Returns:
            The entity if found, None otherwise
        """
        if entity_type == Vehicle:
            return await self.get_vehicle_by_id(entity_id)
        elif entity_type == Driver:
            return await self.get_driver_by_id(entity_id)
        elif entity_type == FleetTransaction or issubclass(entity_type, FleetTransaction):
            return await self.get_transaction_by_id(entity_id)
        else:
            raise ValueError(f"Unsupported entity type: {entity_type}")
    
    async def update_entity(self, entity: T) -> T:
        """
        Generic method to update any entity in the database.
        
        Args:
            entity: The entity to update
            
        Returns:
            The updated entity
            
        Raises:
            ValueError: If entity doesn't exist or has invalid references
        """
        if isinstance(entity, Vehicle):
            return await self.update_vehicle(entity)
        elif isinstance(entity, Driver):
            return await self.update_driver(entity)
        elif isinstance(entity, FleetTransaction):
            return await self.update_transaction(entity)
        else:
            raise ValueError(f"Unsupported entity type: {type(entity)}")
    
    async def delete_entity(self, entity_type: Type[T], entity_id: str) -> bool:
        """
        Generic method to delete any entity from the database.
        
        Args:
            entity_type: The type of entity to delete
            entity_id: The ID of the entity
            
        Returns:
            True if entity was deleted, False if it didn't exist
            
        Raises:
            ValueError: If entity exists but can't be deleted (e.g., has dependencies)
        """
        if entity_type == Vehicle:
            return await self.delete_vehicle(entity_id)
        elif entity_type == Driver:
            return await self.delete_driver(entity_id)
        elif entity_type == FleetTransaction or issubclass(entity_type, FleetTransaction):
            return await self.delete_transaction(entity_id)
        else:
            raise ValueError(f"Unsupported entity type: {entity_type}")
    
    async def _populate_test_data(self) -> None:
        """
        Populate the database with test data for development and testing.
        This method is implemented in the concrete MockDB class.
        """
        pass 