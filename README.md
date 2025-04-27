# FleetSight

FleetSight is a modern fleet management system designed to help organizations monitor and manage their vehicle fleets efficiently.

## Features

- Vehicle management (tracking, maintenance, status)
- Driver management
- Trip and route tracking
- Fuel consumption monitoring
- Maintenance scheduling
- Reporting and analytics
- User authentication and authorization

## Project Structure

```
fleetsight/
├── backend/               # FastAPI backend
│   ├── api/               # API routes
│   ├── models/            # Pydantic models
│   ├── services/          # Business logic
│   └── main.py            # Application entry point
└── frontend/              # Frontend application (future)
```

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fleetsight.git
cd fleetsight
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
uvicorn backend.main:app --reload
```

4. Open your browser and navigate to:
```
http://localhost:8000/docs
```

## API Documentation

Once the server is running, you can access the OpenAPI documentation at:
```
http://localhost:8000/docs
```

## License

[MIT](LICENSE) 