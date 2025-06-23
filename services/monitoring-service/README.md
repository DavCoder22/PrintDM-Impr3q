# Monitoring Service

Microservice for real-time monitoring of printers and their status.

## Features

- Real-time status monitoring
- Alerting system
- Performance metrics collection
- Historical data storage

## API Endpoints

- `GET /monitoring/status`: Get current system status
- `GET /monitoring/metrics`: Get performance metrics
- `GET /monitoring/alerts`: List active alerts
- `POST /monitoring/alerts`: Create a new alert
- `GET /monitoring/history`: Get historical data

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
