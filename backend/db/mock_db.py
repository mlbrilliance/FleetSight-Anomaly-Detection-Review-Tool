"""
MockDB Implementation for the FleetSight Backend
[OWL: fleetsight-system.ttl#MockDatabase]

This module implements a mock database with in-memory storage that adheres to 
all database interfaces defined in backend.db.interface. It provides a complete
implementation suitable for testing and development.

The module maintains full ontology compliance and properly implements all required
interfaces for transactions, vehicles, and drivers.
"""
import asyncio
import copy
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Type, TypeVar, Optional, Any, Generic, cast

from shared_models.models import (
    FleetTransaction, FuelTransaction, MaintenanceTransaction,
    Vehicle, Driver, Entity
)
from backend.db.interface import (
    DBInterface, TransactionRepository, VehicleRepository, DriverRepository
)
from backend.db.mock_db_core import MockDBCore
from backend.db.mock_db_vehicle import MockDBVehicle
from backend.db.mock_db_driver import MockDBDriver
from backend.db.mock_db_transaction import MockDBTransaction

T = TypeVar('T', bound=Entity)


class MockDB(MockDBVehicle, MockDBDriver, MockDBTransaction):
    """
    Mock database implementation with in-memory storage.
    
    This class combines all repository interfaces and maintains
    referential integrity between entities. It includes transaction
    support for atomicity.
    
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
    
    # Vehicle Repository Implementation
    
    async def create_vehicle(self, vehicle: Vehicle) -> Vehicle:
        """
        Create a new vehicle in the database.
        
        Args:
            vehicle: The vehicle to create
            
        Returns:
            The created vehicle
            
        Raises:
            ValueError: If a vehicle with the same ID already exists
        """
        # Check if vehicle with same ID already exists
        if vehicle.vehicle_id in self._vehicles:
            raise ValueError(f"Vehicle with ID {vehicle.vehicle_id} already exists")
        
        # Ensure vehicle has UUID
        if not hasattr(vehicle, 'uuid') or not vehicle.uuid:
            vehicle_dict = vehicle.dict()
            vehicle_dict['uuid'] = uuid.uuid4()
            vehicle = Vehicle(**vehicle_dict)
        
        # Store the vehicle
        self._vehicles[vehicle.vehicle_id] = vehicle
        if vehicle.uuid:
            self._vehicle_uuids[vehicle.uuid] = vehicle.vehicle_id
        
        return vehicle
    
    async def get_vehicle_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        """
        Retrieve a vehicle by its ID.
        
        Args:
            vehicle_id: The ID of the vehicle
            
        Returns:
            The vehicle if found, None otherwise
        """
        return self._vehicles.get(vehicle_id)
    
    async def get_all_vehicles(self, limit: int = 100, offset: int = 0) -> List[Vehicle]:
        """
        Retrieve all vehicles with pagination.
        
        Args:
            limit: Maximum number of vehicles to return
            offset: Number of vehicles to skip
            
        Returns:
            List of vehicles
        """
        vehicles = list(self._vehicles.values())
        return vehicles[offset:offset+limit]
    
    async def update_vehicle(self, vehicle: Vehicle) -> Vehicle:
        """
        Update an existing vehicle.
        
        Args:
            vehicle: The vehicle with updated data
            
        Returns:
            The updated vehicle
            
        Raises:
            ValueError: If the vehicle doesn't exist
        """
        # Check if vehicle exists
        existing_vehicle = self._vehicles.get(vehicle.vehicle_id)
        if not existing_vehicle:
            raise ValueError(f"Vehicle with ID {vehicle.vehicle_id} does not exist")
        
        # Preserve UUID
        if not hasattr(vehicle, 'uuid') or not vehicle.uuid:
            vehicle_dict = vehicle.dict()
            vehicle_dict['uuid'] = existing_vehicle.uuid
            vehicle = Vehicle(**vehicle_dict)
        
        # Update vehicle
        self._vehicles[vehicle.vehicle_id] = vehicle
        
        # Update UUID lookup if needed
        if vehicle.uuid and existing_vehicle.uuid != vehicle.uuid:
            if existing_vehicle.uuid in self._vehicle_uuids:
                del self._vehicle_uuids[existing_vehicle.uuid]
            self._vehicle_uuids[vehicle.uuid] = vehicle.vehicle_id
        
        return vehicle
    
    async def delete_vehicle(self, vehicle_id: str) -> bool:
        """
        Delete a vehicle by its ID.
        
        Args:
            vehicle_id: The ID of the vehicle
            
        Returns:
            True if the vehicle was deleted, False if it didn't exist
            
        Raises:
            ValueError: If the vehicle has associated transactions
        """
        # Check if vehicle exists
        vehicle = self._vehicles.get(vehicle_id)
        if not vehicle:
            return False
        
        # Check for transactions referencing this vehicle
        for txn in self._transactions.values():
            if txn.vehicle_id == vehicle_id:
                raise ValueError(f"Cannot delete vehicle with ID {vehicle_id} as it has associated transactions")
        
        # Remove vehicle from storage
        del self._vehicles[vehicle_id]
        
        # Remove from UUID lookup
        if hasattr(vehicle, 'uuid') and vehicle.uuid and vehicle.uuid in self._vehicle_uuids:
            del self._vehicle_uuids[vehicle.uuid]
        
        return True
    
    # Driver Repository Implementation
    
    async def create_driver(self, driver: Driver) -> Driver:
        """
        Create a new driver in the database.
        
        Args:
            driver: The driver to create
            
        Returns:
            The created driver
            
        Raises:
            ValueError: If a driver with the same ID already exists
            ValueError: If the driver has assigned vehicles that don't exist
        """
        # Check if driver with same ID already exists
        if driver.driver_id in self._drivers:
            raise ValueError(f"Driver with ID {driver.driver_id} already exists")
        
        # Validate vehicle assignments
        if driver.assigned_vehicle_ids:
            for v_id in driver.assigned_vehicle_ids:
                if v_id not in self._vehicles:
                    raise ValueError(f"Cannot assign driver to non-existent vehicle {v_id}")
        
        # Ensure driver has UUID
        if not hasattr(driver, 'uuid') or not driver.uuid:
            driver_dict = driver.dict()
            driver_dict['uuid'] = uuid.uuid4()
            driver = Driver(**driver_dict)
        
        # Store the driver
        self._drivers[driver.driver_id] = driver
        if driver.uuid:
            self._driver_uuids[driver.uuid] = driver.driver_id
        
        return driver
    
    async def get_driver_by_id(self, driver_id: str) -> Optional[Driver]:
        """
        Retrieve a driver by its ID.
        
        Args:
            driver_id: The ID of the driver
            
        Returns:
            The driver if found, None otherwise
        """
        return self._drivers.get(driver_id)
    
    async def get_all_drivers(self, limit: int = 100, offset: int = 0) -> List[Driver]:
        """
        Retrieve all drivers with pagination.
        
        Args:
            limit: Maximum number of drivers to return
            offset: Number of drivers to skip
            
        Returns:
            List of drivers
        """
        drivers = list(self._drivers.values())
        return drivers[offset:offset+limit]
    
    async def get_drivers_by_vehicle(self, vehicle_id: str) -> List[Driver]:
        """
        Retrieve all drivers assigned to a specific vehicle.
        
        Args:
            vehicle_id: The ID of the vehicle
            
        Returns:
            List of drivers assigned to the vehicle
        """
        return [
            driver for driver in self._drivers.values()
            if driver.assigned_vehicle_ids and vehicle_id in driver.assigned_vehicle_ids
        ]
    
    async def update_driver(self, driver: Driver) -> Driver:
        """
        Update an existing driver.
        
        Args:
            driver: The driver with updated data
            
        Returns:
            The updated driver
            
        Raises:
            ValueError: If the driver doesn't exist
            ValueError: If the driver has assigned vehicles that don't exist
        """
        # Check if driver exists
        existing_driver = self._drivers.get(driver.driver_id)
        if not existing_driver:
            raise ValueError(f"Driver with ID {driver.driver_id} does not exist")
        
        # Validate vehicle assignments
        if driver.assigned_vehicle_ids:
            for v_id in driver.assigned_vehicle_ids:
                if v_id not in self._vehicles:
                    raise ValueError(f"Cannot assign driver to non-existent vehicle {v_id}")
        
        # Preserve UUID
        if not hasattr(driver, 'uuid') or not driver.uuid:
            driver_dict = driver.dict()
            driver_dict['uuid'] = existing_driver.uuid
            driver = Driver(**driver_dict)
        
        # Update driver
        self._drivers[driver.driver_id] = driver
        
        # Update UUID lookup if needed
        if driver.uuid and existing_driver.uuid != driver.uuid:
            if existing_driver.uuid in self._driver_uuids:
                del self._driver_uuids[existing_driver.uuid]
            self._driver_uuids[driver.uuid] = driver.driver_id
        
        return driver
    
    async def delete_driver(self, driver_id: str) -> bool:
        """
        Delete a driver by its ID.
        
        Args:
            driver_id: The ID of the driver
            
        Returns:
            True if the driver was deleted, False if it didn't exist
        """
        # Check if driver exists
        driver = self._drivers.get(driver_id)
        if not driver:
            return False
        
        # Remove driver from storage
        del self._drivers[driver_id]
        
        # Remove from UUID lookup
        if hasattr(driver, 'uuid') and driver.uuid and driver.uuid in self._driver_uuids:
            del self._driver_uuids[driver.uuid]
        
        return True
    
    # Transaction Repository Implementation
    
    async def create_transaction(self, transaction: FleetTransaction) -> FleetTransaction:
        """
        Create a new transaction in the database.
        
        Args:
            transaction: The transaction to create
            
        Returns:
            The created transaction
            
        Raises:
            ValueError: If a transaction with the same ID already exists
            ValueError: If the transaction references vehicles or drivers that don't exist
        """
        # Check if transaction with same ID already exists
        if transaction.transaction_id in self._transactions:
            raise ValueError(f"Transaction with ID {transaction.transaction_id} already exists")
        
        # Validate vehicle reference
        if transaction.vehicle_id and transaction.vehicle_id not in self._vehicles:
            raise ValueError(f"Vehicle with ID {transaction.vehicle_id} does not exist")
        
        # Validate driver reference
        if transaction.driver_id and transaction.driver_id not in self._drivers:
            raise ValueError(f"Driver with ID {transaction.driver_id} does not exist")
        
        # Ensure transaction has UUID
        if not hasattr(transaction, 'uuid') or not transaction.uuid:
            transaction_dict = transaction.dict()
            transaction_dict['uuid'] = uuid.uuid4()
            
            # Recreate with the appropriate type
            if isinstance(transaction, FuelTransaction):
                transaction = FuelTransaction(**transaction_dict)
            elif isinstance(transaction, MaintenanceTransaction):
                transaction = MaintenanceTransaction(**transaction_dict)
            else:
                transaction = FleetTransaction(**transaction_dict)
        
        # Store the transaction
        self._transactions[transaction.transaction_id] = transaction
        if transaction.uuid:
            self._transaction_uuids[transaction.uuid] = transaction.transaction_id
        
        return transaction
    
    async def get_transaction_by_id(self, transaction_id: str) -> Optional[FleetTransaction]:
        """
        Retrieve a transaction by its ID.
        
        Args:
            transaction_id: The ID of the transaction
            
        Returns:
            The transaction if found, None otherwise
        """
        return self._transactions.get(transaction_id)
    
    async def get_transactions_by_filter(
        self, filter_params: Dict[str, Any], limit: int = 100, offset: int = 0
    ) -> List[FleetTransaction]:
        """
        Retrieve transactions that match the filter parameters with pagination.
        
        Args:
            filter_params: Key-value pairs for filtering transactions
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            
        Returns:
            List of matching transactions
        """
        # Filter transactions based on parameters
        filtered_transactions = []
        
        for txn in self._transactions.values():
            matches = True
            
            for key, value in filter_params.items():
                if hasattr(txn, key):
                    txn_value = getattr(txn, key)
                    if txn_value != value:
                        matches = False
                        break
                else:
                    matches = False
                    break
            
            if matches:
                filtered_transactions.append(txn)
        
        # Apply pagination
        return filtered_transactions[offset:offset+limit]
    
    async def get_transactions_by_vehicle(
        self, vehicle_id: str, limit: int = 100, offset: int = 0
    ) -> List[FleetTransaction]:
        """
        Retrieve all transactions for a specific vehicle.
        
        Args:
            vehicle_id: The ID of the vehicle
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            
        Returns:
            List of transactions for the vehicle
        """
        return await self.get_transactions_by_filter(
            filter_params={"vehicle_id": vehicle_id},
            limit=limit,
            offset=offset
        )
    
    async def get_transactions_by_driver(
        self, driver_id: str, limit: int = 100, offset: int = 0
    ) -> List[FleetTransaction]:
        """
        Retrieve all transactions for a specific driver.
        
        Args:
            driver_id: The ID of the driver
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            
        Returns:
            List of transactions for the driver
        """
        return await self.get_transactions_by_filter(
            filter_params={"driver_id": driver_id},
            limit=limit,
            offset=offset
        )
    
    async def get_fuel_transactions(
        self, filter_params: Dict[str, Any], limit: int = 100, offset: int = 0
    ) -> List[FuelTransaction]:
        """
        Retrieve fuel transactions that match the filter parameters with pagination.
        
        Args:
            filter_params: Key-value pairs for filtering transactions
            limit: Maximum number of transactions to return
            offset: Number of transactions to skip
            
        Returns:
            List of matching fuel transactions
        """
        # Filter transactions to get only FuelTransaction instances
        filtered_transactions = []
        
        for txn in self._transactions.values():
            if not isinstance(txn, FuelTransaction):
                continue
            
            matches = True
            for key, value in filter_params.items():
                if hasattr(txn, key):
                    txn_value = getattr(txn, key)
                    if txn_value != value:
                        matches = False
                        break
                else:
                    matches = False
                    break
            
            if matches:
                filtered_transactions.append(txn)
        
        # Apply pagination
        return filtered_transactions[offset:offset+limit]
    
    async def update_transaction(self, transaction: FleetTransaction) -> FleetTransaction:
        """
        Update an existing transaction.
        
        Args:
            transaction: The transaction with updated data
            
        Returns:
            The updated transaction
            
        Raises:
            ValueError: If the transaction doesn't exist
            ValueError: If the transaction references vehicles or drivers that don't exist
        """
        # Check if transaction exists
        existing_transaction = self._transactions.get(transaction.transaction_id)
        if not existing_transaction:
            raise ValueError(f"Transaction with ID {transaction.transaction_id} does not exist")
        
        # Validate vehicle reference
        if transaction.vehicle_id and transaction.vehicle_id not in self._vehicles:
            raise ValueError(f"Vehicle with ID {transaction.vehicle_id} does not exist")
        
        # Validate driver reference
        if transaction.driver_id and transaction.driver_id not in self._drivers:
            raise ValueError(f"Driver with ID {transaction.driver_id} does not exist")
        
        # Ensure consistent type between original and update
        if type(transaction) != type(existing_transaction):
            raise ValueError(f"Cannot change transaction type from {type(existing_transaction)} to {type(transaction)}")
        
        # Preserve UUID
        if not hasattr(transaction, 'uuid') or not transaction.uuid:
            transaction_dict = transaction.dict()
            transaction_dict['uuid'] = existing_transaction.uuid
            
            # Recreate with the appropriate type
            if isinstance(transaction, FuelTransaction):
                transaction = FuelTransaction(**transaction_dict)
            elif isinstance(transaction, MaintenanceTransaction):
                transaction = MaintenanceTransaction(**transaction_dict)
            else:
                transaction = FleetTransaction(**transaction_dict)
        
        # Update transaction
        self._transactions[transaction.transaction_id] = transaction
        
        # Update UUID lookup if needed
        if transaction.uuid and existing_transaction.uuid != transaction.uuid:
            if existing_transaction.uuid in self._transaction_uuids:
                del self._transaction_uuids[existing_transaction.uuid]
            self._transaction_uuids[transaction.uuid] = transaction.transaction_id
        
        return transaction
    
    async def delete_transaction(self, transaction_id: str) -> bool:
        """
        Delete a transaction by its ID.
        
        Args:
            transaction_id: The ID of the transaction
            
        Returns:
            True if the transaction was deleted, False if it didn't exist
        """
        # Check if transaction exists
        transaction = self._transactions.get(transaction_id)
        if not transaction:
            return False
        
        # Remove transaction from storage
        del self._transactions[transaction_id]
        
        # Remove from UUID lookup
        if hasattr(transaction, 'uuid') and transaction.uuid and transaction.uuid in self._transaction_uuids:
            del self._transaction_uuids[transaction.uuid]
        
        return True
    
    async def batch_create_transactions(self, transactions: List[FleetTransaction]) -> List[FleetTransaction]:
        """
        Create multiple transactions in a batch.
        
        Args:
            transactions: List of transactions to create
            
        Returns:
            List of created transactions
            
        Raises:
            ValueError: If any transaction is invalid
        """
        # Start a transaction for atomicity
        await self.begin_transaction()
        
        created_transactions = []
        try:
            for txn in transactions:
                created = await self.create_transaction(txn)
                created_transactions.append(created)
            
            # Commit the changes
            await self.commit_transaction()
            
        except Exception as e:
            # Rollback on any error
            await self.rollback_transaction()
            raise e
        
        return created_transactions
    
    async def _populate_test_data(self) -> None:
        """
        Populate the database with test data for development and testing.
        Creates sample vehicles, drivers, and transactions.
        """
        # Create test vehicles
        vehicles = [
            Vehicle(
                vehicle_id="V001",
                make="Toyota",
                model="Camry",
                year=2020,
                vehicle_type="Sedan",
                fuel_capacity=Decimal("15.0"),
                fuel_capacity_unit="gallon"
            ),
            Vehicle(
                vehicle_id="V002",
                make="Ford",
                model="F-150",
                year=2019,
                vehicle_type="Truck",
                fuel_capacity=Decimal("26.0"),
                fuel_capacity_unit="gallon"
            ),
            Vehicle(
                vehicle_id="V003",
                make="Tesla",
                model="Model 3",
                year=2021,
                vehicle_type="EV",
                fuel_capacity=Decimal("75.0"),
                fuel_capacity_unit="kWh"
            )
        ]
        
        for vehicle in vehicles:
            await self.create_vehicle(vehicle)
        
        # Create test drivers
        drivers = [
            Driver(
                driver_id="D001",
                name="John Doe",
                license_number="DL12345",
                assigned_vehicle_ids=["V001"]
            ),
            Driver(
                driver_id="D002",
                name="Jane Smith",
                license_number="DL67890",
                assigned_vehicle_ids=["V002"]
            ),
            Driver(
                driver_id="D003",
                name="Bob Johnson",
                license_number="DL54321",
                assigned_vehicle_ids=["V003", "V001"]  # Multiple assignments
            )
        ]
        
        for driver in drivers:
            await self.create_driver(driver)
        
        # Create test transactions
        now = datetime.now()
        
        transactions = [
            # Fuel transactions
            FuelTransaction(
                transaction_id="T001",
                timestamp=now,
                amount=Decimal("45.00"),
                currency="USD",
                merchant_name="Shell Gas Station",
                merchant_category="Fuel",
                latitude=40.7128,
                longitude=-74.0060,
                vehicle_id="V001",
                driver_id="D001",
                fuel_type="Regular",
                fuel_volume=Decimal("15.0"),
                fuel_volume_unit="gallon",
                odometer_reading=12500
            ),
            FuelTransaction(
                transaction_id="T002",
                timestamp=now,
                amount=Decimal("65.00"),
                currency="USD",
                merchant_name="Exxon Gas Station",
                merchant_category="Fuel",
                latitude=34.0522,
                longitude=-118.2437,
                vehicle_id="V002",
                driver_id="D002",
                fuel_type="Regular",
                fuel_volume=Decimal("21.7"),
                fuel_volume_unit="gallon",
                odometer_reading=45000
            ),
            # Maintenance transactions
            MaintenanceTransaction(
                transaction_id="T003",
                timestamp=now,
                amount=Decimal("120.00"),
                currency="USD",
                merchant_name="Quick Lube",
                merchant_category="Maintenance",
                latitude=41.8781,
                longitude=-87.6298,
                vehicle_id="V001",
                driver_id="D001",
                maintenance_type="Oil Change",
                odometer_reading=12600
            ),
            MaintenanceTransaction(
                transaction_id="T004",
                timestamp=now,
                amount=Decimal("750.00"),
                currency="USD",
                merchant_name="AutoFix Shop",
                merchant_category="Maintenance",
                latitude=37.7749,
                longitude=-122.4194,
                vehicle_id="V002",
                driver_id="D002",
                maintenance_type="Brake Service",
                odometer_reading=45100
            ),
            # EV charging transaction
            FuelTransaction(
                transaction_id="T005",
                timestamp=now,
                amount=Decimal("25.00"),
                currency="USD",
                merchant_name="Tesla Supercharger",
                merchant_category="Fuel",
                latitude=47.6062,
                longitude=-122.3321,
                vehicle_id="V003",
                driver_id="D003",
                fuel_type="Electricity",
                fuel_volume=Decimal("50.0"),
                fuel_volume_unit="kWh",
                odometer_reading=8000
            )
        ]
        
        await self.batch_create_transactions(transactions) 