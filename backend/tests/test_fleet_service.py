"""
Tests for the fleet service.
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import patch, MagicMock

from backend.models.fleet import Fleet, FleetCreate, FleetUpdate
from backend.services.fleet_service import FleetService


@pytest.mark.asyncio
async def test_get_all_fleets(mock_supabase):
    """Test getting all fleets."""
    # Arrange
    fleet_service = FleetService()
    
    # Act
    fleets = await fleet_service.get_all_fleets()
    
    # Assert
    assert len(fleets) == 1
    assert fleets[0].id == "123e4567-e89b-12d3-a456-426614174002"
    assert fleets[0].name == "Main Fleet"
    assert fleets[0].location == "Headquarters"
    assert fleets[0].vehicle_count == 5
    assert fleets[0].driver_count == 8


@pytest.mark.asyncio
async def test_get_fleet_by_id(mock_supabase):
    """Test getting a fleet by ID."""
    # Arrange
    fleet_service = FleetService()
    fleet_id = "123e4567-e89b-12d3-a456-426614174002"
    
    # Act
    fleet = await fleet_service.get_fleet_by_id(fleet_id)
    
    # Assert
    assert fleet is not None
    assert fleet.id == fleet_id
    assert fleet.name == "Main Fleet"
    assert fleet.description == "Primary fleet of company vehicles"
    assert fleet.location == "Headquarters"
    assert fleet.status == "active"


@pytest.mark.asyncio
async def test_get_fleet_by_id_not_found(mock_supabase):
    """Test getting a fleet by ID when the fleet doesn't exist."""
    # Arrange
    fleet_service = FleetService()
    fleet_id = "non-existent-id"
    
    # Configure the mock to return empty data for this ID
    with patch('backend.db.supabase_client.get_supabase_client') as mock_get_client:
        mock_client = MagicMock()
        mock_table = MagicMock()
        mock_table.select.return_value.__aenter__.return_value = MagicMock(data=[])
        mock_client.table.return_value = mock_table
        mock_get_client.return_value = mock_client
        
        # Act/Assert
        with pytest.raises(ValueError, match="Fleet not found"):
            await fleet_service.get_fleet_by_id(fleet_id)


@pytest.mark.asyncio
async def test_create_fleet(mock_supabase):
    """Test creating a fleet."""
    # Arrange
    fleet_service = FleetService()
    fleet_create = FleetCreate(
        name="Secondary Fleet",
        description="Secondary fleet for the sales team",
        location="Sales Office",
        manager_id="123e4567-e89b-12d3-a456-426614174003",
        status="active",
        vehicle_count=3,
        driver_count=5,
        notes="New fleet for the expanded sales team"
    )
    
    # Act
    new_fleet = await fleet_service.create_fleet(fleet_create)
    
    # Assert
    assert new_fleet is not None
    assert new_fleet.id is not None
    assert new_fleet.name == "Secondary Fleet"
    assert new_fleet.description == "Secondary fleet for the sales team"
    assert new_fleet.location == "Sales Office"
    assert new_fleet.status == "active"


@pytest.mark.asyncio
async def test_update_fleet(mock_supabase):
    """Test updating a fleet."""
    # Arrange
    fleet_service = FleetService()
    fleet_id = "123e4567-e89b-12d3-a456-426614174002"
    fleet_update = FleetUpdate(
        name="Main Fleet",
        description="Updated description for the main fleet",
        vehicle_count=6,
        driver_count=9,
        notes="Updated after expansion"
    )
    
    # Act
    updated_fleet = await fleet_service.update_fleet(fleet_id, fleet_update)
    
    # Assert
    assert updated_fleet is not None
    assert updated_fleet.id == fleet_id
    assert updated_fleet.description == "Updated description for the main fleet"
    assert updated_fleet.vehicle_count == 6
    assert updated_fleet.driver_count == 9
    assert updated_fleet.notes == "Updated after expansion"


@pytest.mark.asyncio
async def test_delete_fleet(mock_supabase):
    """Test deleting a fleet."""
    # Arrange
    fleet_service = FleetService()
    fleet_id = "123e4567-e89b-12d3-a456-426614174002"
    
    # Act
    result = await fleet_service.delete_fleet(fleet_id)
    
    # Assert
    assert result is True


@pytest.mark.asyncio
async def test_get_fleet_stats(mock_supabase):
    """Test getting fleet statistics."""
    # Arrange
    fleet_service = FleetService()
    fleet_id = "123e4567-e89b-12d3-a456-426614174002"
    
    # Act
    stats = await fleet_service.get_fleet_stats(fleet_id)
    
    # Assert
    assert stats is not None
    assert stats.total_vehicles == 5
    assert stats.active_vehicles == 4
    assert stats.total_drivers == 8
    assert stats.active_drivers == 7
    assert stats.total_distance == 8500
    assert stats.total_fuel_consumed == 950
    assert stats.total_maintenance_cost == 3500
    assert stats.fleet_efficiency_score == 88.5


@pytest.mark.asyncio
async def test_get_fleet_stats_not_found(mock_supabase):
    """Test getting stats for a fleet that doesn't exist."""
    # Arrange
    fleet_service = FleetService()
    fleet_id = "non-existent-id"
    
    # Act
    stats = await fleet_service.get_fleet_stats(fleet_id)
    
    # Assert
    assert stats is not None
    assert stats.total_vehicles == 0
    assert stats.active_vehicles == 0
    assert stats.total_drivers == 0
    assert stats.active_drivers == 0
    assert stats.total_distance == 0
    assert stats.total_fuel_consumed == 0
    assert stats.total_maintenance_cost == 0
    assert stats.fleet_efficiency_score == 0.0 