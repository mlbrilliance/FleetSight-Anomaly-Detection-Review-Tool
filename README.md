# FleetSight - Fleet Management and Anomaly Detection Platform

FleetSight is a comprehensive fleet management platform with integrated anomaly detection capabilities. The system helps fleet managers monitor vehicles, track drivers, manage transactions, and identify unusual patterns or issues.

## Features

- **Vehicle Management**: Track and manage your entire fleet of vehicles
- **Driver Management**: Maintain driver information, assignments, and status
- **Transaction Tracking**: Record and analyze fuel and maintenance transactions
- **Anomaly Detection**: Identify unusual patterns in fleet operations
- **Data Visualization**: View comprehensive reports and dashboards

## Project Structure

```
fleetsight/
├── backend/              # Backend API and business logic
│   ├── api/              # API routes and endpoints
│   ├── db/               # Database models and interface
│   │   ├── interface.py  # Abstract DB interface
│   │   └── mock_db.py    # Mock implementation for testing
│   └── tests/            # Backend tests
│       ├── test_mock_db.py
│       └── ...
├── frontend/             # Frontend application (to be implemented)
├── shared_models/        # Shared Pydantic models
│   └── models.py         # Core entity models
└── owl/                  # Ontology definitions
```

## Getting Started

### Prerequisites

- Python 3.11+
- Git

### Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mlbrilliance/FleetSight-Anomaly-Detection-Review-Tool.git
   cd FleetSight-Anomaly-Detection-Review-Tool
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run tests:
   ```bash
   python -m pytest
   ```

### Development with GitHub Codespaces

1. Navigate to the repository on GitHub
2. Click the "Code" button and select the "Codespaces" tab
3. Click "Create codespace on main"
4. The development environment will set up automatically with all required dependencies

## Testing

Run the test suite:

```bash
python -m pytest
```

Or run specific test files:

```bash
python -m pytest backend/tests/test_mock_db.py
```

## License

[MIT](LICENSE)

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request 