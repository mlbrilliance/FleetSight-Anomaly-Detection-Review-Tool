"""
Run script for the FleetSight application.

This script is used to start the FleetSight application using Uvicorn or run tests.
"""

import sys
import uvicorn
import subprocess

def print_usage():
    """Print script usage information."""
    print("FleetSight Runner")
    print("Usage:")
    print("  python run.py [command]")
    print("")
    print("Commands:")
    print("  run         Start the FastAPI application (default)")
    print("  test        Run all tests")
    print("  test_api    Run API tests")
    print("  test_unit   Run unit tests")

if __name__ == "__main__":
    # Get command line arguments
    args = sys.argv[1:] 
    command = args[0] if args else "run"
    
    if command == "run":
        # Start the FastAPI application
        print("Starting FleetSight API...")
        uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
    
    elif command == "test":
        # Run all tests
        print("Running all tests...")
        subprocess.run(["pytest", "-v", "backend/tests/"])
    
    elif command == "test_api":
        # Run API tests
        print("Running API tests...")
        subprocess.run(["pytest", "-v", "backend/tests/test_vehicle_api.py"])
    
    elif command == "test_unit":
        # Run unit tests
        print("Running unit tests...")
        subprocess.run(["pytest", "-v", "backend/tests/test_fleet_service.py"])
    
    else:
        print(f"Unknown command: {command}")
        print_usage() 