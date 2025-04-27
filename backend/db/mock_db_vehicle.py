"""
MockDB Vehicle Repository Implementation for FleetSight Backend
[OWL: fleetsight-system.ttl#VehicleRepository]

This module implements the vehicle repository functionality of the mock database,
providing CRUD operations for vehicle entities.
"""
import uuid
from typing import Dict, List, Optional

from shared_models.models import Vehicle
from backend.db.interface import VehicleRepository
from backend.db.mock_db_core import MockDBCore


class MockDBVehicle(MockDBCore):
    """
    Mock database implementation for vehicle repository functionality.
    
    This class extends MockDBCore and implements the VehicleRepository interface
    for vehicle entity operations.
    
    [OWL: fleetsight-system.ttl#VehicleRepository]
    """
    
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