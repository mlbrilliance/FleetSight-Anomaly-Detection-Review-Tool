"""
Database interface.

This module defines the abstract interface for database interactions,
ensuring consistency across different implementations (Supabase, mock, etc.).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar

from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class DatabaseInterface(Generic[T], ABC):
    """
    Abstract interface for database operations.
    
    All database implementations (Supabase, mock, etc.) should implement this interface.
    """
    
    @abstractmethod
    async def get_by_id(self, model_type: Type[T], id_value: str) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            model_type: The Pydantic model type.
            id_value: The entity ID.
            
        Returns:
            Entity if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_all(self, model_type: Type[T]) -> List[T]:
        """
        Get all entities of type.
        
        Args:
            model_type: The Pydantic model type.
            
        Returns:
            List of entities.
        """
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> Tuple[bool, Optional[T]]:
        """
        Create entity.
        
        Args:
            entity: The entity to create.
            
        Returns:
            Tuple of (success, created_entity).
        """
        pass
    
    @abstractmethod
    async def batch_create(self, entities: List[T]) -> Tuple[bool, List[T]]:
        """
        Create multiple entities.
        
        Args:
            entities: The entities to create.
            
        Returns:
            Tuple of (success, created_entities).
        """
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> Tuple[bool, Optional[T]]:
        """
        Update entity.
        
        Args:
            entity: The entity to update.
            
        Returns:
            Tuple of (success, updated_entity).
        """
        pass
    
    @abstractmethod
    async def delete(self, model_type: Type[T], id_value: str) -> bool:
        """
        Delete entity.
        
        Args:
            model_type: The Pydantic model type.
            id_value: The entity ID.
            
        Returns:
            Success status.
        """
        pass
    
    @abstractmethod
    async def query(self, model_type: Type[T], query_params: Dict[str, Any]) -> List[T]:
        """
        Query entities.
        
        Args:
            model_type: The Pydantic model type.
            query_params: Query parameters.
            
        Returns:
            List of entities matching query.
        """
        pass 