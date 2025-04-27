"""
Tests for the fleet service.
"""

import pytest
from datetime import datetime

from backend.models.fleet import FleetCreate, FleetUpdate
from backend.services.fleet_service import FleetService


@pytest.mark.asyncio
async def test_get_fleets(mock_supabase):
    """Test getting all fleets."""
    service = FleetService()
    fleets = await service.get_fleets()
    
    assert len(fleets) == 1
    assert fleets[0].name == "Main Fleet"
    assert fleets[0].description == "Our main operational fleet"
    assert fleets[0].status == "active"


@pytest.mark.asyncio
async def test_get_fleet(mock_supabase):
    """Test getting a specific fleet."""
    service = FleetService()
    fleet = await service.get_fleet("123e4567-e89b-12d3-a456-426614174002")
    
    assert fleet is not None
    assert fleet.id == "123e4567-e89b-12d3-a456-426614174002"
    assert fleet.name == "Main Fleet"
    assert fleet.description == "Our main operational fleet"
    assert fleet.status == "active"


@pytest.mark.asyncio
async def test_get_nonexistent_fleet(mock_supabase):
    """Test getting a nonexistent fleet."""
    service = FleetService()
    fleet = await service.get_fleet("non-existent-id")
    
    assert fleet is None


@pytest.mark.asyncio
async def test_create_fleet(mock_supabase):
    """Test creating a new fleet."""
    service = FleetService()
    new_fleet = FleetCreate(
        organization_id="123e4567-e89b-12d3-a456-426614174005",
        name="Secondary Fleet",
        description="Our secondary delivery fleet",
        status="active",
        address="123 Business Park, Commerce City, USA",
        contact_name="Jane Manager",
        contact_email="jane.manager@example.com",
        contact_phone="555-876-5432",
        max_vehicles=25,
        notes="This fleet handles short-distance deliveries"
    )
    
    created_fleet = await service.create_fleet(new_fleet)
    
    assert created_fleet is not None
    assert created_fleet.organization_id == "123e4567-e89b-12d3-a456-426614174005"
    assert created_fleet.name == "Secondary Fleet"
    assert created_fleet.description == "Our secondary delivery fleet"
    assert created_fleet.status == "active"
    assert created_fleet.address == "123 Business Park, Commerce City, USA"
    assert created_fleet.contact_name == "Jane Manager"
    
    # Check if the fleet was added to the database
    all_fleets = await service.get_fleets()
    assert len(all_fleets) == 2


@pytest.mark.asyncio
async def test_update_fleet(mock_supabase):
    """Test updating a fleet."""
    service = FleetService()
    fleet_id = "123e4567-e89b-12d3-a456-426614174002"
    
    update_data = FleetUpdate(
        name="Updated Main Fleet",
        description="Our updated main operational fleet",
        status="maintenance",
        contact_name="John Manager",
        contact_email="john.manager@example.com",
        contact_phone="555-123-9876",
        notes="This fleet is currently undergoing annual maintenance"
    )
    
    updated_fleet = await service.update_fleet(fleet_id, update_data)
    
    assert updated_fleet is not None
    assert updated_fleet.id == fleet_id
    assert updated_fleet.name == "Updated Main Fleet"
    assert updated_fleet.description == "Our updated main operational fleet"
    assert updated_fleet.status == "maintenance"
    assert updated_fleet.contact_name == "John Manager"
    assert updated_fleet.contact_email == "john.manager@example.com"
    assert updated_fleet.contact_phone == "555-123-9876"
    assert updated_fleet.notes == "This fleet is currently undergoing annual maintenance"
    
    # Check if the fleet was updated in the database
    fleet = await service.get_fleet(fleet_id)
    assert fleet.name == "Updated Main Fleet"
    assert fleet.description == "Our updated main operational fleet"
    assert fleet.status == "maintenance"
    assert fleet.contact_name == "John Manager"
    assert fleet.contact_email == "john.manager@example.com"
    assert fleet.contact_phone == "555-123-9876"
    assert fleet.notes == "This fleet is currently undergoing annual maintenance"


@pytest.mark.asyncio
async def test_update_nonexistent_fleet(mock_supabase):
    """Test updating a nonexistent fleet."""
    service = FleetService()
    
    update_data = FleetUpdate(
        name="Updated Nonexistent Fleet",
        status="maintenance"
    )
    
    updated_fleet = await service.update_fleet("non-existent-id", update_data)
    
    assert updated_fleet is None


@pytest.mark.asyncio
async def test_delete_fleet(mock_supabase):
    """Test deleting a fleet."""
    service = FleetService()
    fleet_id = "123e4567-e89b-12d3-a456-426614174002"
    
    # Verify the fleet exists before deletion
    fleet_before = await service.get_fleet(fleet_id)
    assert fleet_before is not None
    
    # Delete the fleet
    result = await service.delete_fleet(fleet_id)
    assert result is True
    
    # Verify the fleet no longer exists
    fleet_after = await service.get_fleet(fleet_id)
    assert fleet_after is None


@pytest.mark.asyncio
async def test_delete_nonexistent_fleet(mock_supabase):
    """Test deleting a nonexistent fleet."""
    service = FleetService()
    
    result = await service.delete_fleet("non-existent-id")
    assert result is False


@pytest.mark.asyncio
async def test_get_fleets_by_organization(mock_supabase):
    """Test getting fleets by organization ID."""
    service = FleetService()
    organization_id = "123e4567-e89b-12d3-a456-426614174005"
    
    fleets = await service.get_fleets_by_organization(organization_id)
    
    assert len(fleets) == 1
    assert fleets[0].organization_id == organization_id
    assert fleets[0].name == "Main Fleet"
    
    # Test with nonexistent organization ID
    fleets = await service.get_fleets_by_organization("non-existent-org")
    assert len(fleets) == 0


@pytest.mark.asyncio
async def test_get_fleets_by_status(mock_supabase):
    """Test getting fleets by status."""
    service = FleetService()
    
    # Test with existing status
    fleets = await service.get_fleets_by_status("active")
    assert len(fleets) == 1
    assert fleets[0].status == "active"
    
    # Test with nonexistent status
    fleets = await service.get_fleets_by_status("non-existent-status")
    assert len(fleets) == 0


@pytest.mark.asyncio
async def test_get_fleet_stats(mock_supabase):
    """Test getting fleet statistics."""
    service = FleetService()
    fleet_id = "123e4567-e89b-12d3-a456-426614174002"
    
    stats = await service.get_fleet_stats(fleet_id)
    
    assert stats is not None
    assert stats.get("total_vehicles") == 5
    assert stats.get("active_vehicles") == 4
    assert stats.get("total_drivers") == 6
    assert stats.get("active_drivers") == 5
    assert stats.get("total_trips") == 150
    assert stats.get("total_distance") == 7500
    assert stats.get("fuel_consumption") == 750
    assert stats.get("maintenance_count") == 12
    assert stats.get("operating_cost") == 15000.00
    
    # Test with nonexistent fleet ID
    stats = await service.get_fleet_stats("non-existent-fleet")
    assert stats is not None
    assert stats.get("total_vehicles") == 0
    assert stats.get("active_vehicles") == 0
    assert stats.get("total_drivers") == 0
    assert stats.get("active_drivers") == 0
    assert stats.get("total_trips") == 0
    assert stats.get("total_distance") == 0
    assert stats.get("fuel_consumption") == 0
    assert stats.get("maintenance_count") == 0
    assert stats.get("operating_cost") == 0.0 