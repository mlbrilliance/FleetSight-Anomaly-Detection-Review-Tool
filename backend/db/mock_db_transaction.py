"""
MockDB Transaction Repository Implementation for FleetSight Backend
[OWL: fleetsight-system.ttl#TransactionRepository]

This module implements the transaction repository functionality of the mock database,
providing CRUD operations for transaction entities.
"""
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime

from shared_models.models import (
    FleetTransaction, FuelTransaction, MaintenanceTransaction
)
from backend.db.interface import TransactionRepository
from backend.db.mock_db_core import MockDBCore


class MockDBTransaction(MockDBCore):
    """
    Mock database implementation for transaction repository functionality.
    
    This class extends MockDBCore and implements the TransactionRepository interface
    for transaction entity operations.
    
    [OWL: fleetsight-system.ttl#TransactionRepository]
    """
    
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