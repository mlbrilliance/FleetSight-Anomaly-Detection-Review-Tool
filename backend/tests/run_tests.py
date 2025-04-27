#!/usr/bin/env python
"""
Test runner script for FleetSight backend.
[OWL: fleetsight-core-entities.ttl]

This script runs all the tests for the FleetSight backend, including both
pytest-based tests and direct tests. It provides a simple way to run
all tests with proper configuration.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(project_root))


def run_pytest_tests(verbose=False, test_path=None):
    """
    Run pytest-based tests.
    
    Args:
        verbose: Whether to run in verbose mode
        test_path: Optional specific test path to run
    
    Returns:
        True if all tests passed, False otherwise
    """
    print("\n📋 Running pytest-based tests...")
    
    # Build command
    cmd = [sys.executable, "-m", "pytest"]
    
    if verbose:
        cmd.append("-v")
        
    # Add test discovery path
    if test_path:
        cmd.append(test_path)
    else:
        cmd.append("backend/tests/")
    
    # Add coverage reporting
    cmd.extend(["--cov=backend", "--cov-report=term"])
    
    # Run the tests
    result = subprocess.run(cmd, cwd=str(project_root))
    return result.returncode == 0


def run_direct_tests(verbose=False):
    """
    Run direct test scripts that don't use pytest.
    
    Args:
        verbose: Whether to run in verbose mode
    
    Returns:
        True if all tests passed, False otherwise
    """
    print("\n🔍 Running direct tests...")
    
    direct_tests = [
        "backend/tests/processing/direct_test.py"
    ]
    
    all_passed = True
    
    for test_script in direct_tests:
        script_path = os.path.join(project_root, test_script)
        print(f"\nRunning direct test: {test_script}")
        
        # Build command
        cmd = [sys.executable, script_path]
        if verbose:
            cmd.append("--verbose")
            
        # Run the test
        result = subprocess.run(cmd, cwd=str(project_root))
        if result.returncode != 0:
            all_passed = False
            print(f"❌ Test failed: {test_script}")
        else:
            print(f"✅ Test passed: {test_script}")
    
    return all_passed


def main():
    """Run all tests and report results."""
    parser = argparse.ArgumentParser(description="Run FleetSight backend tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--pytest-only", action="store_true", help="Run only pytest tests")
    parser.add_argument("--direct-only", action="store_true", help="Run only direct tests")
    parser.add_argument("--path", help="Specific test path to run")
    
    args = parser.parse_args()
    
    print("🚀 Starting FleetSight backend tests...\n")
    
    pytest_passed = True
    direct_passed = True
    
    # Run pytest tests if requested
    if not args.direct_only:
        pytest_passed = run_pytest_tests(args.verbose, args.path)
    
    # Run direct tests if requested
    if not args.pytest_only and not args.path:
        direct_passed = run_direct_tests(args.verbose)
    
    # Print summary
    print("\n📊 Test Summary:")
    if not args.direct_only:
        print(f"  - Pytest Tests: {'✅ PASSED' if pytest_passed else '❌ FAILED'}")
    if not args.pytest_only and not args.path:
        print(f"  - Direct Tests: {'✅ PASSED' if direct_passed else '❌ FAILED'}")
    
    # Return exit code
    if pytest_passed and direct_passed:
        print("\n✅ All tests passed successfully!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 