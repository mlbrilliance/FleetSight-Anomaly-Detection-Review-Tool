"""
MockDB Driver Repository Implementation for FleetSight Backend
[OWL: fleetsight-system.ttl#DriverRepository]

This module implements the driver repository functionality of the mock database,
providing CRUD operations for driver entities.
"""
import uuid
from typing import Dict, List, Optional

from shared_models.models import Driver
from backend.db.interface import DriverRepository
from backend.db.mock_db_core import MockDBCore


class MockDBDriver(MockDBCore):
    """
    Mock database implementation for driver repository functionality.
    
    This class extends MockDBCore and implements the DriverRepository interface
    for driver entity operations.
    
    [OWL: fleetsight-system.ttl#DriverRepository]
    """
    
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