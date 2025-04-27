# FleetSight Backend Tests

This directory contains tests for the FleetSight backend components. The tests are designed to validate the correctness of different modules in the backend system.

## Test Structure

The test directory is organized according to the backend module structure:

```
backend/tests/
├── api/                   # Tests for API endpoints
│   ├── routes/            # Tests for specific route modules
│   └── auth/              # Tests for authentication
├── processing/            # Tests for data processing modules
├── models/                # Tests for data models
├── repositories/          # Tests for data repositories
├── conftest.py            # Shared pytest fixtures and utilities
├── run_tests.py           # Test runner script
└── README.md              # This file
```

## Running Tests

You can run the tests using the provided `run_tests.py` script, which handles both pytest-based tests and direct tests:

```bash
# Run all tests
python backend/tests/run_tests.py

# Run with verbose output
python backend/tests/run_tests.py -v

# Run only pytest tests
python backend/tests/run_tests.py --pytest-only

# Run only direct tests
python backend/tests/run_tests.py --direct-only

# Run specific tests
python backend/tests/run_tests.py --path backend/tests/api/routes/test_transaction_routes.py
```

Alternatively, you can run pytest directly:

```bash
# Run all pytest tests with coverage
pytest backend/tests/ --cov=backend --cov-report=term

# Run specific test file
pytest backend/tests/processing/test_cleaner.py
```

## Key Test Modules

### Transaction Routes Tests

The `backend/tests/api/routes/test_transaction_routes.py` file contains comprehensive tests for all transaction API endpoints. These tests cover:

- GET, POST, PUT, and DELETE operations for transactions
- Batch transaction creation
- Transaction processing for anomaly detection
- Filtering transactions by driver, vehicle, and date range
- Error handling for invalid requests

These tests use mocks for the repository layer and dependency injection to isolate the API functionality.

### Transaction Processing Tests

Two test files cover the transaction processing functionality:

1. `backend/tests/processing/test_cleaner.py` - Pytest-based tests for the transaction preprocessing module, including:
   - Extraction of time-related features
   - Location feature processing
   - Fuel and maintenance type feature extraction
   - Text field cleaning
   - Transaction history feature derivation
   - Validation of the ProcessedTransaction model

2. `backend/tests/processing/direct_test.py` - Direct tests that validate the same preprocessing functionality without pytest dependencies, useful for quick verification.

## Test Types

The project uses two types of tests:

### 1. Pytest-based Tests

Most tests use the pytest framework and follow these principles:

- Tests are organized by module/functionality
- Each test module focuses on a specific component
- Fixtures in `conftest.py` provide common test data and mocks
- [OWL] references are included in docstrings to maintain semantic connections

### 2. Direct Tests

Some modules are tested using direct test scripts that don't rely on pytest. These are standalone Python scripts that:

- Can be run directly with Python
- Include self-contained test logic and assertions
- Report pass/fail results based on assertions

The following direct tests are available:

- `processing/direct_test.py`: Tests core processing functionality without pytest dependencies

## Adding New Tests

When adding new tests:

1. Follow the existing directory structure (mirror the backend module structure)
2. Include [OWL] references in docstrings when relevant
3. Use fixtures from `conftest.py` when possible
4. Add comprehensive test cases covering normal operation and edge cases
5. If adding a new direct test, update `run_tests.py` to include it

## Test Coverage

The tests aim to provide comprehensive coverage of the backend codebase. When running with coverage reporting, you'll see statistics about which parts of the code are covered by tests.

To generate a detailed HTML coverage report:

```bash
pytest backend/tests/ --cov=backend --cov-report=html
```

This will create a `htmlcov` directory with a browsable coverage report. 