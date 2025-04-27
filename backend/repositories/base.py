"""
Base repository interface definition.

This module defines the abstract base class for all repositories.
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Type, TypeVar

from uuid import UUID

T = TypeVar('T')


class BaseRepository(Generic[T], ABC):
    """
    Abstract base repository interface.
    
    Defines the standard CRUD operations for any repository.
    """
    
    @abstractmethod
    async def create(self, item: T) -> T:
        """
        Create a new item.
        
        Args:
            item: The item to create.
            
        Returns:
            The created item.
        """
        pass
    
    @abstractmethod
    async def get(self, id: UUID) -> Optional[T]:
        """
        Get an item by ID.
        
        Args:
            id: The ID of the item to get.
            
        Returns:
            The item if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Get a list of items.
        
        Args:
            skip: The number of items to skip.
            limit: The maximum number of items to return.
            
        Returns:
            A list of items.
        """
        pass
    
    @abstractmethod
    async def update(self, id: UUID, item: T) -> Optional[T]:
        """
        Update an item.
        
        Args:
            id: The ID of the item to update.
            item: The updated item.
            
        Returns:
            The updated item if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """
        Delete an item.
        
        Args:
            id: The ID of the item to delete.
            
        Returns:
            True if the item was deleted, False otherwise.
        """
        pass 