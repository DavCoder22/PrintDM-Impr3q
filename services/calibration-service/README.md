# Calibration Service

Microservice for managing printer calibration processes.

## Features

- Calibration profile management
- Automatic calibration routines
- Calibration history tracking
- Printer-specific calibration settings

## API Endpoints

- `POST /calibration/start`: Start a new calibration
- `GET /calibration/{calibration_id}`: Get calibration status
- `GET /calibration/printer/{printer_id}`: Get calibration history for a printer
- `POST /calibration/profiles`: Create a new calibration profile
- `GET /calibration/profiles/{profile_id}`: Get calibration profile details

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

## Environment Variables

- `APP_ENV`: Environment (dev, test, prod)
- `DATABASE_URL`: Database connection string
- `LOG_LEVEL`: Logging level (debug, info, warning, error, critical)
