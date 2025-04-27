"""
API router module.

This module registers all API routes.
"""

from fastapi import APIRouter

from backend.api.routes import (
    auth_routes,
    driver_routes,
    fleet_routes,
    maintenance_routes,
    transaction_routes,
    vehicle_routes,
)

# Create the main API router
api_router = APIRouter(prefix="/api")

# Register all routes
api_router.include_router(auth_routes.router)
api_router.include_router(driver_routes.router)
api_router.include_router(fleet_routes.router)
api_router.include_router(maintenance_routes.router)
api_router.include_router(transaction_routes.router)
api_router.include_router(vehicle_routes.router) 