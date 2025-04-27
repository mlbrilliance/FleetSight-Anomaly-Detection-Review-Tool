"""
Mock Supabase client for testing.

This module provides a mock implementation of the Supabase client for testing.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from unittest.mock import MagicMock


class MockSupabaseQueryBuilder:
    """Mock query builder for Supabase client."""

    def __init__(self, table_name: str, data: List[Dict[str, Any]]):
        """
        Initialize the query builder.
        
        Args:
            table_name: The name of the table.
            data: The data in the table.
        """
        self.table_name = table_name
        self.data = data
        self.filtered_data = data.copy()
        self.filter_conditions = []

    def select(self, *columns) -> "MockSupabaseQueryBuilder":
        """Mock select operation."""
        return self

    def insert(self, data: Dict[str, Any]) -> "MockSupabaseQueryBuilder":
        """Mock insert operation."""
        self.insert_data = data
        return self

    def update(self, data: Dict[str, Any]) -> "MockSupabaseQueryBuilder":
        """Mock update operation."""
        self.update_data = data
        return self

    def delete(self) -> "MockSupabaseQueryBuilder":
        """Mock delete operation."""
        self.delete_flag = True
        return self

    def eq(self, column: str, value: Any) -> "MockSupabaseQueryBuilder":
        """Mock equals filter."""
        self.filtered_data = [
            item for item in self.filtered_data 
            if item.get(column) == value
        ]
        return self

    def neq(self, column: str, value: Any) -> "MockSupabaseQueryBuilder":
        """Mock not equals filter."""
        self.filtered_data = [
            item for item in self.filtered_data 
            if item.get(column) != value
        ]
        return self

    def gte(self, column: str, value: Any) -> "MockSupabaseQueryBuilder":
        """Mock greater than or equal filter."""
        self.filtered_data = [
            item for item in self.filtered_data 
            if item.get(column) and item.get(column) >= value
        ]
        return self

    def lte(self, column: str, value: Any) -> "MockSupabaseQueryBuilder":
        """Mock less than or equal filter."""
        self.filtered_data = [
            item for item in self.filtered_data 
            if item.get(column) and item.get(column) <= value
        ]
        return self

    def range(self, start: int, end: int) -> "MockSupabaseQueryBuilder":
        """Mock range pagination."""
        self.filtered_data = self.filtered_data[start:end+1]
        return self

    def execute(self) -> Dict[str, Any]:
        """
        Execute the query and return results.
        """
        response = {"data": None, "count": None, "error": None}
        
        if hasattr(self, "insert_data"):
            # Handle insert operation
            new_item = self.insert_data.copy()
            if "id" not in new_item:
                new_item["id"] = str(uuid4())
            if "created_at" not in new_item:
                new_item["created_at"] = "2023-07-01T12:00:00Z"
            if "updated_at" not in new_item:
                new_item["updated_at"] = "2023-07-01T12:00:00Z"
                
            self.data.append(new_item)
            response["data"] = [new_item]
        
        elif hasattr(self, "update_data"):
            # Handle update operation
            for item in self.filtered_data:
                for key, value in self.update_data.items():
                    item[key] = value
                item["updated_at"] = "2023-07-01T13:00:00Z"
            response["data"] = self.filtered_data
        
        elif hasattr(self, "delete_flag"):
            # Handle delete operation
            deleted_items = self.filtered_data.copy()
            for item in deleted_items:
                if item in self.data:
                    self.data.remove(item)
            response["data"] = deleted_items
        
        else:
            # Handle select operation
            response["data"] = self.filtered_data
            
        return type('obj', (object,), response)


class MockUser:
    """Mock user object."""
    
    def __init__(self, id: str, email: str):
        """Initialize the user."""
        self.id = id
        self.email = email


class MockAuth:
    """Mock auth module for Supabase client."""
    
    def __init__(self):
        """Initialize the auth module."""
        self.current_user = MockUser(
            id="123e4567-e89b-12d3-a456-426614174000",
            email="test@example.com"
        )
    
    def get_user(self, token: str) -> Dict[str, Any]:
        """
        Mock get user from token.
        
        Args:
            token: The authentication token.
            
        Returns:
            A mock user.
        """
        # In a real implementation, this would verify the token and return the user
        if token == "test_token":
            return type('obj', (object,), {"user": self.current_user})
        return type('obj', (object,), {"user": None})


class MockSupabaseClient:
    """Mock Supabase client for testing."""
    
    def __init__(self, *args, **kwargs):
        """Initialize the mock client."""
        self.auth = MagicMock()
        self._tables = {}
        
        # Mock auth methods
        self.auth.sign_in_with_password = MagicMock(return_value=MagicMock(
            user={"id": "test-user-id", "email": "test@example.com"}
        ))
        
    def table(self, table_name):
        """Get a table by name."""
        if table_name not in self._tables:
            self._tables[table_name] = MockTable(table_name)
        return self._tables[table_name]


class MockTable:
    """Mock Supabase table for testing."""
    
    def __init__(self, name):
        """Initialize the mock table."""
        self.name = name
        self._data = []
        self._filters = []
        
    def select(self, *columns):
        """Select columns from the table."""
        return self
        
    def eq(self, column, value):
        """Filter by equality."""
        self._filters.append((column, value))
        return self
        
    def execute(self):
        """Execute the query."""
        # Apply filters to the data
        filtered_data = self._data
        for column, value in self._filters:
            filtered_data = [item for item in filtered_data if item.get(column) == value]
            
        # Clear filters for next query
        self._filters = []
        
        # Return mock response
        response = MagicMock()
        response.data = filtered_data
        return response
        
    def insert(self, data):
        """Insert data into the table."""
        if isinstance(data, list):
            self._data.extend(data)
        else:
            self._data.append(data)
            
        # Return mock response
        response = MagicMock()
        response.data = [data] if not isinstance(data, list) else data
        return self
        
    def update(self, data):
        """Update data in the table."""
        return self

    def seed_data(self, table_name: str, data: List[Dict[str, Any]]) -> None:
        """
        Seed data into a table.
        
        Args:
            table_name: The name of the table.
            data: The data to seed.
        """
        self._tables[table_name] = data 