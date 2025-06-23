# Printers Service

Microservice for managing printers and their operations.

## Features

- List all printers
- Get printer status
- Add/remove printers
- Update printer configuration

## API Endpoints

- `GET /printers`: List all printers
- `GET /printers/{printer_id}`: Get printer details
- `POST /printers`: Add a new printer
- `PUT /printers/{printer_id}`: Update printer
- `DELETE /printers/{printer_id}`: Remove printer

## Development

### Prerequisites

- Python 3.9+
- Poetry (for dependency management)

### Setup

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Run the service:
   ```bash
   uvicorn app.main:app --reload
   ```

### Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=term-missing
```

## Environment Variables

- `APP_ENV`: Environment (dev, test, prod)
- `DATABASE_URL`: Database connection string
- `LOG_LEVEL`: Logging level (debug, info, warning, error, critical)
