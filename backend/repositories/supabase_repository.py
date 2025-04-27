"""
Supabase repository implementation.

This module implements the repository interface using Supabase.
"""

from datetime import datetime
from typing import Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID

import httpx
from pydantic import BaseModel

from backend.config import settings
from backend.repositories.base import BaseRepository

T = TypeVar('T', bound=BaseModel)


class SupabaseRepository(BaseRepository[T], Generic[T]):
    """
    Supabase repository implementation.
    
    Implements the repository interface using Supabase as the backend.
    """
    
    def __init__(self, model_cls: Type[T], table_name: str):
        """
        Initialize the repository.
        
        Args:
            model_cls: The model class.
            table_name: The name of the table in Supabase.
        """
        self.model_cls = model_cls
        self.table_name = table_name
        self.base_url = f"{settings.supabase_url}/rest/v1"
        self.headers = {
            "apikey": settings.supabase_key,
            "Authorization": f"Bearer {settings.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    async def create(self, item: T) -> T:
        """
        Create a new item in Supabase.
        
        Args:
            item: The item to create.
            
        Returns:
            The created item.
        """
        async with httpx.AsyncClient() as client:
            item_dict = item.dict(exclude_unset=True, exclude={"id"} if item.id is None else set())
            response = await client.post(
                f"{self.base_url}/{self.table_name}",
                json=item_dict,
                headers=self.headers
            )
            response.raise_for_status()
            return self.model_cls(**response.json()[0])
    
    async def get(self, id: UUID) -> Optional[T]:
        """
        Get an item by ID from Supabase.
        
        Args:
            id: The ID of the item to get.
            
        Returns:
            The item if found, None otherwise.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{self.table_name}",
                params={"id": f"eq.{id}"},
                headers=self.headers
            )
            response.raise_for_status()
            items = response.json()
            return self.model_cls(**items[0]) if items else None
    
    async def list(self, skip: int = 0, limit: int = 100) -> List[T]:
        """
        Get a list of items from Supabase.
        
        Args:
            skip: The number of items to skip.
            limit: The maximum number of items to return.
            
        Returns:
            A list of items.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{self.table_name}",
                headers={
                    **self.headers,
                    "Range": f"{skip}-{skip + limit - 1}"
                }
            )
            response.raise_for_status()
            return [self.model_cls(**item) for item in response.json()]
    
    async def update(self, id: UUID, item: T) -> Optional[T]:
        """
        Update an item in Supabase.
        
        Args:
            id: The ID of the item to update.
            item: The updated item.
            
        Returns:
            The updated item if found, None otherwise.
        """
        async with httpx.AsyncClient() as client:
            item_dict = item.dict(exclude_unset=True, exclude={"id", "created_at"})
            item_dict["updated_at"] = datetime.now().isoformat()
            
            response = await client.patch(
                f"{self.base_url}/{self.table_name}",
                params={"id": f"eq.{id}"},
                json=item_dict,
                headers=self.headers
            )
            response.raise_for_status()
            
            items = response.json()
            return self.model_cls(**items[0]) if items else None
    
    async def delete(self, id: UUID) -> bool:
        """
        Delete an item from Supabase.
        
        Args:
            id: The ID of the item to delete.
            
        Returns:
            True if the item was deleted, False otherwise.
        """
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/{self.table_name}",
                params={"id": f"eq.{id}"},
                headers=self.headers
            )
            response.raise_for_status()
            return response.status_code == 204 