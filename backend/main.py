"""
Main application entry point.

This module sets up the FastAPI application and includes all routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI app.
    
    This handles startup and shutdown events.
    """
    # Startup
    print("Starting application...")
    yield
    # Shutdown
    print("Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title="FleetSight API",
    description="API for FleetSight fleet management system",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the API router that contains all route modules
app.include_router(api_router)


@app.get("/")
async def root():
    """
    Root endpoint.
    
    Returns a welcome message.
    """
    return {"message": "Welcome to FleetSight API"}


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns the status of the application.
    """
    return {"status": "healthy"} 