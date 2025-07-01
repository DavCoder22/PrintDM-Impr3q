# PrintDM - Distributed Printing Management System

A distributed system for managing 3D printers, monitoring print jobs, and handling automatic calibration.

## Project Structure

```
PrintDM-Impr3q/
├── services/                    # Microservices
│   ├── printers-service/       # Printers management and specifications
│   ├── monitoring-service/     # Print job monitoring and status management
│   └── calibration-service/    # Automatic calibration management
├── terraform/                  # Infrastructure as Code
├── scripts/                    # Utility scripts
├── requirements.txt            # Main project dependencies
├── requirements-dev.txt        # Development dependencies
└── docker-compose.yml          # Docker Compose configuration
```

## Dependency Management

This project uses a centralized dependency management system:

- `requirements.txt`: Contains all production dependencies for the entire project
- `requirements-dev.txt`: Contains additional development dependencies (testing, linting, etc.)

### Setting Up the Environment

1. Create and activate a virtual environment:


   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```


2. Install dependencies:

   ```bash
   # For production
   pip install -r requirements.txt
   
   # For development (includes testing and linting tools)
   pip install -r requirements-dev.txt
   ```

### Running Tests

To run tests for all services:

```bash
# From the project root
./scripts/run_tests.sh
```

## Services Overview

### 1. Printers Service

- Manages printer information and specifications
- Tracks print volume and usage
- Provides printer status and capabilities

**Port:** 8000

### 2. Calibration Service

- Tracks print counts
- Manages automatic calibration alerts (after 3 prints)
- Handles calibration history

**Port:** 8001

### 3. Monitoring Service

- Manages print jobs and their status
- Handles printer status updates
- Provides real-time monitoring of print jobs
- Integrates with calibration service for alerts

**Port:** 8002

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.9+

## Getting Started

1. Clone the repository
2. Start the services:
   ```bash
   docker-compose up -d
   ```
3. Access the services:

   - **Printers Service:** [http://localhost:8000](http://localhost:8000)
   - **Monitoring Service:** [http://localhost:8002](http://localhost:8002)
   - **Calibration Service:** [http://localhost:8001](http://localhost:8001)
   - **PostgreSQL:** `localhost:5432`
   - **pgAdmin:** [http://localhost:5050](http://localhost:5050) (admin@example.com/admin)

## Key Features

### Print Job Management

- Create and track print jobs
- Monitor print progress in real-time
- Pause/resume/cancel print jobs
- Automatic timeout detection

### Printer Status

- Real-time status updates
- Automatic calibration alerts
- Print volume tracking
- Detailed printer specifications

### Calibration System

- Automatic calibration alerts after 3 prints
- Calibration history tracking
- Integration with printer status

## API Documentation

Each service provides interactive OpenAPI documentation:

- **Printers Service API:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Monitoring Service API:** [http://localhost:8002/docs](http://localhost:8002/docs)
- **Calibration Service API:** [http://localhost:8001/docs](http://localhost:8001/docs)

## Development

### Setting Up Development Environment

1. Create a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix/macOS:
   source venv/bin/activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r services/<service-name>/requirements-dev.txt
   ```

### Running Tests

To run tests for a specific service:
```bash
cd services/<service-name>
pytest -v --cov=app tests/
```

To run all tests with coverage:
```bash
./scripts/run_tests.sh
```

## Service Interactions

1. **Starting a Print Job:**
   - Monitoring Service creates a new print job
   - Updates printer status to "printing"
   - Tracks print progress

2. **Print Completion:**
   - Monitoring Service marks job as completed
   - Updates printer status
   - Notifies Calibration Service of print completion

3. **Calibration Alert:**
   - After 3 prints, Calibration Service triggers an alert
   - Updates printer status to "calibration_needed"
   - Monitoring Service shows alert in dashboard

## Environment Variables

### Printers Service

- `DATABASE_URL`: PostgreSQL connection string
- `LOG_LEVEL`: Logging level (default: info)

### Monitoring Service

- `DATABASE_URL`: PostgreSQL connection string
- `PRINTERS_SERVICE_URL`: URL of Printers Service (default: `http://printers-service:8000`)
- `CALIBRATION_SERVICE_URL`: URL of Calibration Service (default: `http://calibration-service:8000`)
- `LOG_LEVEL`: Logging level (default: info)

### Calibration Service

- `DATABASE_URL`: PostgreSQL connection string
- `PRINTERS_SERVICE_URL`: URL of Printers Service (default: `http://printers-service:8000`)
- `LOG_LEVEL`: Logging level (default: info)

## Deployment

### Docker Compose


```bash
docker-compose up -d --build
```


### Kubernetes (Optional)

See the `kubernetes/` directory for deployment manifests.

## License

MIT License

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
