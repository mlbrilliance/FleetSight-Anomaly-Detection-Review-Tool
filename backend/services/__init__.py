"""
Services package initialization.

This file marks the directory as a Python package.
"""

# Import all service modules
from backend.services.user_service import authenticate_user, get_user_by_email

# Import service modules as they are added
# from backend.services.fleet_service import get_vehicles, get_vehicle_by_id, create_vehicle, update_vehicle, delete_vehicle

__all__ = ["authenticate_user", "get_user_by_email"] 