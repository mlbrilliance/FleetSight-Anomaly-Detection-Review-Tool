"""
Routes package initialization.

This file marks the directory as a Python package.

This module imports all route modules for the API.
"""

# Import route modules as they are implemented
# from backend.api.routes import vehicles

# Force import all route modules to register them with the router
from backend.api.routes import (
    auth_routes,
    driver_routes,
    fleet_routes,
    maintenance_routes,
    transaction_routes,
    vehicle_routes,
) 